# NAS uploader

## Зависимости

    pip3 install pysmb Flask

## Запуск

    cd
    git clone https://git.miem.hse.ru/19102/nas-uploader.git
    cd nas-uploader

Необходимо отредактировать файл `app/config.json` в соответствии с хранилищем, к которому нужно подключиться. 

- `username` и `password` - конфеденциальная информация для входа
- `ip` - ip-адрес хранилища
- `share_name` - общая папка доступа
- `path` - изначальный путь к папке (можно оставить пустым)
- `source_path` - путь с выгружаемым файлам, считая от папки репозитория (указать `/home/jetson/Videos`)

Для запуска используется команда:
    
    flask run --host=0.0.0.0

## Использование

... потом...
