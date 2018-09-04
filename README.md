## UsynoviteP
#### Author: Timofeev Alexey, 2018
#### email: buzzin@mail.ru


Скрипт для парсинга сайта www.usynovite.ru и отправки новых анкет в чат/канал Telegram

Инструкция по настройке и запуску расчитана на ОС CentOS 7.x

Я рекомендую запускать скрипт в контейнере Docker

#### Установка Docker

    yum install -y yum-utils device-mapper-persistent-data lvm2
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum-config-manager --enable docker-ce-edge
    yum install docker-ce
    systemctl enable docker
    systemctl start docker

#### Настройка

    cd /opt/
    git clone
    cd /opt/UsynoviteP
    mkdir logs
    mkdir data
    touch secret.py

#### Отредактировать файл secret.py

    chat_id = "XXX"   #ID чата в который будут отсылаться анкеты         
    token = "YYY"     #ID бота в Telegram
    
#### Создание образа docker
    
    docker build -t usynovitep .
   
#### Запуск образа

    docker run -v /opt/UsynoviteP:/app usynovitep:latest
    