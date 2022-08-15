import datetime
import os, json
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure


def connect(user_name, passwd, ip, port):
    samba = None
    status = False
    try:
        while not status:
            samba = SMBConnection(user_name, passwd, '', '', use_ntlm_v2=True)
            samba.connect(ip, port)
            status = samba.auth_result
    except:
        samba.close()
    return samba, status


def all_shares_name(samba):
    share_names = list()
    sharelist = samba.listShares()
    for s in sharelist:
        share_names.append(s.name)
    return share_names


def all_file_names_in_dir(samba, service_name, dir_name, is_directory=False, timeout=30):
    f_names = list()
    for e in samba.listPath(service_name, dir_name, timeout):
        if e.filename[0] != '.':
            if e.isDirectory == is_directory:
                f_names.append(e.filename)
    return f_names


def get_last_updatetime(samba, service_name, file_path):
    try:
        sharedfile_obj = samba.getAttributes(service_name, file_path)
        return sharedfile_obj.last_write_time
    except OperationFailure:
        return 0


def download(samba, f_names, service_name, smb_dir, local_dir):
    assert isinstance(f_names, list)
    for f_name in f_names:
        f = open(os.path.join(local_dir, f_name), 'wb')
        samba.retrieveFile(service_name, os.path.join(smb_dir, f_name), f)
        f.close()


def createDir(samba, service_name, path):
    try:
        samba.createDirectory(service_name, path)
    except OperationFailure:
        pass


def upload(samba, service_name, smb_dir, local_dir, f_names):
    assert isinstance(f_names, list)
    for f_name in f_names:
        print(f'filename: {f_name}')
        with open(os.path.join(local_dir, f_name), 'rb') as f:
            dest_path = smb_dir + '/' + f_name
            #dest_path = '\:'.join(dest_path.split(':'))
            #dest_path = dest_path.encode('utf-8') 

            print(f'dest_path: {dest_path}')
            try:
                samba.storeFile(service_name, dest_path, f)
            except Exception:
                print('cant storeFile')
                raise


if __name__ == '__main__':
    with open('app/config.json') as config_file:
        config = json.load(config_file)
    samba, status = connect(config['username'], config['password'], config['ip'], config['port'])
    if status:
        print('smb connented')
    else:
        print('smb not connected')
    
    share_names = all_shares_name(samba)
    print("share_names:", share_names)

    share_name = config['share_name']
    dst_name = config['path']
    f_names = all_file_names_in_dir(samba, share_name, dst_name)
    print("share_name: {} -dir_name: {} include f_names:".format(share_name, dst_name), f_names)
    

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
    '''

    samba.close()
