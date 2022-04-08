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

Добавляя это приложение в скрипт аврозапуска, можно спокойно добавить две строчки:

    cd /home/jetson/nas-uploader
    flask run --host=0.0.0.0 &

## Использование

### Доступ с сайту

Главная страница располагается по адресу `http://ip:5000/`, где ip указать тот, что используется машиной, на которой сервер поднят.

### Настройка папки выгрузки

Перейти по ссылке `Configure NAS upload path` для настройки папки выгрузки. Есть кнопка `Submit changes` для установки папки как выгрузной. Для перемещения по диску используется кнопка `Go back` и кнопки с названиями папок в текущей директории. Для возвращении в директорию, что выбрана как папка выгрузки, нажать `Go to default path`. Для создания новой папки ввести её название в свободное поле снизу и нажать кнопку `Create new directory`.

### Выгрузка файлов

Для выгрузки перейти на главную страницу по ссылке `To the main path`, после чего нажать `Upload files`. Загрузка может занят очень продолжительное время - в этот момент идёт выгрузка, - не закрывать и не пытаться перезапустить страницу в этот момент! Пока эта функция синхронная, нужно соблюдать это правило.
