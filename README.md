## UsynoviteP
#### Author: Timofeev Alexey, 2018
#### email: buzzin@mail


Скрипт для парсинга сайта www.usynovite.ru и отправки новых анкет в чат Telegram

Инструкция по настройке и запуску расчитана на ОС Centos 7.x

#### Установка PostgreSQL
    
    yum install https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
    yum install postgresql96-server postgresql96
    /usr/pgsql-9.6/bin/postgresql96-setup initdb
    systemctl start postgresql-9.6.service
    systemctl enable postgresql-9.6.service
    
    Редактирование /var/lin/pgsql/9.6/data/pg_
    

#### Создание базы данных
    
    su postgres
    psql
    create role usynovitedba with login password 'Secret' valid until 'infinity';
    create database usynovitedb with encoding='UTF8' owner=usynovitedba connection limit=-1;
    \q
    psql -U usynovitedba -d usynovitedb
    create table anketa (id int SERIAL, number varchar(20));

#### Установка Python

#### Настройка

    cd /opt
    git pull https://github.com/buzzin5113/UsynoviteP
    cd UsynoviteP
    touch secret.py
    echo "chat_id='Строка-индентификатор чата в Telegram'" >> secret.py
    echo "token='Стройка индекнтификатор бота для постинга в Telegram'" >> secret.py
    echo "db='pq://usynovitedba:Secret@localhost:5432/usynovitedb'
    python3 -m venv ./venv
    source ./bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt 

#### Запуск

    python3 post.py

#### Запуск по cron

python3.6 -m venv /opt/UsynoviteP
source ./bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt

