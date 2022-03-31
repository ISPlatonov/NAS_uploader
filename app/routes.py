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
dst_name = config['path'].split('/')

rel_path = dst_name


'''
file_path = dst_name + '/' + 'Проектный семинар 10-03-2022.mkv'
timestamp = get_last_updatetime(samba, share_name, file_path)
print(datetime.datetime.fromtimestamp(timestamp))


smb_dir = dst_name + '/' + 'Презентация лаборатории сетевых видеотехнологий'
f_names =['лаба итог.prproj', 'Лаба.prproj']
local_dir = ''
download(samba, f_names, share_name, smb_dir, local_dir)

path = smb_dir + '/' + 'aboba'
createDir(samba, share_name, path)

local_dir = '.vscode'
f_names = ['settings.json']
upload(samba, share_name, path, local_dir, f_names)

samba.close()
'''


@app.route('/', methods=['GET'])
def hello_world():
    try:
        return render_template('index.html')
    except Exception as error:
        print(repr(error))
        return "<h1>Error 404</h1><p>{}</p>".format(error)


@app.route('/configure_path', methods=['GET', 'POST'])
def configure_path():
    '''
    try:
        return render_template('configure_path.html')
    except Exception as error:
        print(repr(error))
        return "<h1>Error 404</h1><p>{}</p>".format(error)
    '''
    global rel_path
    dirs = all_file_names_in_dir(samba, share_name, '/'.join(rel_path))
    
    if request.method == 'POST':
        if 'submit_button' in request.form:
            if request.form['submit_button'] == 'Do Something':
                return '<h1>Done something</h1>', 200
            elif request.form['submit_button'] == 'Do Something Else':
                return '<h1>Done something else</h1>', 200
        
        elif 'dir' in request.form:
            if request.form['dir'] in dirs:
                rel_path.append(request.form['dir'])
                dirs = all_file_names_in_dir(samba, share_name, '/'.join(rel_path))
                #return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path))
                return redirect(request.url)

            else:
                return '<h1>Error 404</h1>', 404
        elif 'go_back' in request.form:
            if request.form['go_back'] == 'Go back':
                rel_path.pop()
                dirs = all_file_names_in_dir(samba, share_name, '/'.join(rel_path))
                #return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path))
                return redirect(request.url)
            else:
                return '<h1>Error 404</h1>', 404
        else:
            return '<h1>Error 404</h1>', 404

    elif request.method == 'GET':
        return render_template('configure_path.html', form=request.form, dirs=dirs, share_name=share_name, dst_name='/'.join(rel_path), go_back=not rel_path == [''])
