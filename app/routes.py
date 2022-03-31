from flask import render_template, redirect
from flask.globals import request
from flask.json import jsonify
from app import app
from app.nas import *


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
        print(repr(error))
        return "<h1>Error 404</h1><p>{}</p>".format(error)


@app.route('/upload_files', methods=['GET'])
def upload_files():
    try:
        #files = all_file_names_in_dir(samba, config['share_name'], config['path'])
        #print('files: {}'.format(files))
        local_files = set(os.listdir('video'))
        remote_files = set(all_file_names_in_dir(samba, config['share_name'], config['path']))
        files = list(local_files.difference(remote_files))
        upload(samba, config['share_name'], config['path'], config['source_path'], files) # needs to be async!
        return "<h1>Uploaded!</h1><p>{}</p>".format(files)
    except Exception as error:
        print(repr(error))
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
        else:
            return '<h1>Error 404</h1>', 404

    elif request.method == 'GET':
        return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path), go_back=not rel_path == [''], submit_button=not rel_path == config['path'].split('/'))
