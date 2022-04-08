from flask import render_template, redirect
from flask.globals import request
from flask.json import jsonify
from app import app
from app.nas import *

import re, subprocess


with open('app/config.json') as config_file:
    config = json.load(config_file)

samba, status = connect(config['username'], config['password'], config['ip'], config['port'])

if not status:
    raise ConnectionError("Can't connect to NAS")

share_name = config['share_name']
#dst_name = config['path'].split('/')

rel_path = config['path'].split('/')


@app.route('/', methods=['GET'])
def hello_world():
    try:
        return render_template('index.html')
    except Exception as error:
        return "<h1>Error 404</h1><p>{}</p>".format(error)


@app.route('/upload_files', methods=['GET'])
def upload_files():
    try:
        #files = all_file_names_in_dir(samba, config['share_name'], config['path'])
        #print('files: {}'.format(files))
        local_files = set(os.listdir(config['source_path']))
        remote_files = set(all_file_names_in_dir(samba, config['share_name'], config['path']))
        files = list(local_files.difference(remote_files))

        video_file_regex = re.compile('^\d{3}\ .*\_\d{2}\-\d{2}\-\d{4}\_\d{2}\-\d{2}\-\d{2}\_\d{2}\.mp4$') 
        video_files = [file for file in files if video_file_regex.match(file)]
        
        audio_file_regex = re.compile('^audio\ \d{3}\ .*\_\d{2}\-\d{2}\-\d{4}\_\d{2}\-\d{2}\-\d{2}\_\d{2}\.aac$')
        audio_files = [file for file in files if audio_file_regex.match(file)]
        audio_files_dict = dict()
        for audio_file in audio_files:
            room = audio_file.split()[1]
            if room not in audio_files_dict:
                audio_files_dict[room] = [audio_file]
            else:
                audio_files_dict[room].append(audio_file)

        merged_files = list()
        for video_file in video_files:
            room = video_file.split()[0]
            if room not in audio_files_dict:
                merged_files.append(video_file)
                continue
            audio_files_list = audio_files_dict[room]
            date = '_'.join(''.join(video_file.split('.')[:-1]).split('_')[-3:])
            for afile in audio_files_list:
                if date == '_'.join(''.join(afile.split('.')[:-1]).split('_')[-3:]):
                    audio_file = afile
                else:
                    merged_files.append(video_file)
                    continue
            
            merged_file = 'merged ' + video_file
            command = ['ffmpeg', '-i', config['source_path'] + '/' + audio_file, '-i', config['source_path'] + '/' + video_file, '-c', 'copy', config['source_path'] + '/' +  merged_file]
            subprocess.run(command)
            merged_files.append(merged_file)
            files.append(merged_file)

        upload(samba, config['share_name'], config['path'], config['source_path'], merged_files) # needs to be async!
        for file in files:
            os.remove(config['source_path'] + '/' + file) 
        #return "<h1>Uploaded!</h1><p>{}</p>".format(files)
        return render_template('upload.html', uploaded_files=merged_files)  
    except Exception as error:
        print(type(error))
        print(error.args)
        print(error)
        return "<h1>Error 404</h1><p>{}</p>".format(error)


@app.route('/configure_path', methods=['GET', 'POST'])
def configure_path():
    global rel_path
    dirs = all_file_names_in_dir(samba, share_name, '/'.join(rel_path), is_directory=True)
    
    if request.method == 'POST':
        if 'submit_button' in request.form:
            if request.form['submit_button'] == 'Submit changes':
                with open('app/config.json', 'w') as config_file:
                    config['path'] = '/'.join(rel_path)
                    json.dump(config, config_file)
                return redirect(request.url)
            elif request.form['submit_button'] == 'Go to default path':
                rel_path = config['path'].split('/')
                return redirect(request.url)
            else:
                return '<h1>Error 404</h1>', 404
        
        elif 'dir' in request.form:
            if request.form['dir'] in dirs:
                rel_path.append(request.form['dir'])
                dirs = all_file_names_in_dir(samba, share_name, '/'.join(rel_path), is_directory=True)
                #return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path))
                return redirect(request.url)
            else:
                return '<h1>Error 404</h1>', 404

        elif 'go_back' in request.form:
            if request.form['go_back'] == 'Go back':
                rel_path.pop()
                dirs = all_file_names_in_dir(samba, share_name, '/'.join(rel_path), is_directory=True)
                #return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path))
                return redirect(request.url)
            else:
                return '<h1>Error 404</h1>', 404
        elif 'create_dir' in request.form:
            dir_name = request.form.get('new_dir_name')
            createDir(samba, share_name, '/'.join(rel_path + [dir_name]))
            return redirect(request.url)

        else:
            return '<h1>Error 404</h1>', 404

    elif request.method == 'GET':
        return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path), go_back=not rel_path == [''], submit_button=not rel_path == config['path'].split('/'))
