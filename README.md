# UsynoviteP
# Create Timofeev Alexey 2018
#
# Скрипт для парсинга сайта www.usynovite.ru и отправки новых анкет в чат Telegram
#

# Установка PostgreSQL
yum install https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm
yum install postgresql96-server postgresql96
/usr/pgsql-9.6/bin/postgresql96-setup initdb
systemctl start postgresql-9.6.service
systemctl enable postgresql-9.6.service

# Создание базы данных
su postgres
create role usynovitedba with login password 'Secret' valid until 'infinity';
create database usynovitedb with encoding='UTF8' owner=usynovitedba connection limit=-1;
exit
psql -U usynovitedba -d usynovitedb
create table anketa (id int PRIMARY KEY, number varchar(20));

