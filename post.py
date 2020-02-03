from bs4 import BeautifulSoup
import logging
import os
import re
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import shutil
import sqlite3
import telegram
import time

import secret


def telegram_send_text(msg):
    """
    Send a message to a telegram user specified on chatId
    chat_id must be a number!
    """

    bot = telegram.Bot(secret.token)
    try:
        #bot.sendMessage(secret.chat_id, text=msg,  parse_mode=telegram.ParseMode.HTML)
        time.sleep(5)  # Чтобы не попасть в спам
        return True
    except telegram.TelegramError as error_text:
        logging.error('Ошибка отправки текстового сообщения в телеграм')
        logging.error(error_text)
        return False


def telegram_send_image(url):
    """
    Send a image from url to a telegram user specified on chatId
    chat_id must be a number!
    """

    bot = telegram.Bot(secret.token)
    try:
        #bot.send_photo(secret.chat_id, photo=url)
        time.sleep(5)
        return True
    except telegram.TelegramError as error_text:
        logging.error('Ошибка отправки изображения в телеграм')
        logging.error(error_text)
        msg = "Фотография не найдена"
        #telegram_send_text(msg)
        return False


def select_anketa(db_old, db_new, anketa_id):
    """
    Проверка наличия в БД номера анкеты
    """

    c_old = db_old.cursor()
    c_old.execute("select count(*) from anketa where anketa_id = '{0}'".format(anketa_id))
    count_old = c_old.fetchone()
    
    c_new = db_new.cursor()
    c_new.execute("select count(*) from anketa where anketa_id = '{0}'".format(anketa_id))
    count_new = c_new.fetchone()
    
    print(len(count_old), len(count_new))
    if len(count_old) == 0 and len(count_new) == 0:
        return 1
    else:
        return 0


def insert_anketa(db_new, anketa_id, age):
    """
    Вставка номера анкеты в БД
    """

    c = db_new.cursor()
    c.execute("INSERT INTO anketa VALUES ('{0}','{1}')".format(anketa_id, age))
    db_new.commit()


def logging_set():
    """
    Настройка логгирования
    """
    handlers = [logging.FileHandler('./logs/post{0}.log'.format(time.strftime("%Y%m%d-%H%M%S"))),
                logging.StreamHandler()]
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging.INFO,
                        datefmt='%Y%m%d %H%M%S',
                        handlers=handlers)


def db_old_connect():

    file_path = './data/usynovite_old.db'

    if os.path.exists(file_path):
        conn = sqlite3.connect(file_path)
    else:
        conn = sqlite3.connect(file_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE anketa (anketa_id text, age int)''')

    return conn


def db_new_connect():
    """
    Подключение к БД
    """

    file_path = './data/usynovite_new.db'

    if os.path.exists(file_path):
        conn = sqlite3.connect(file_path)
    else:
        conn = sqlite3.connect(file_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE anketa (anketa_id text, age int)''')

    return conn


def db_close(db_new, db_old):

    db_new.close()
    db_old.close()
    shutil.move('./data/usynovite_old.db', './data/usynovite_old_{0}.db'.format(time.strftime("%Y%m%d-%H%M%S")))
    shutil.move('./data/usynovite_new.db', './data/usynovite_old.db')


def parser(html, db_new, db_old, count):
    """
    Парсинг HTML страницы
    """

    age = 1990
    soup = BeautifulSoup(html, features="html.parser")
    div = soup('div', class_='search-bd__slaider--content')

    for k in div:

        string = str(k)
        start = string.find('/child/?id=')
        anketa_id = string[start+11:start+28]
        anketa_id = anketa_id[:anketa_id.find('"')]

        logging.info("Найдена анкета - {0}: порядковый номер {1}".format(anketa_id, count))
        count += 1

        msg = re.sub('</p>', '\n', str(k))      # Из <p> делаем перевод строки
        msg = re.sub('<[^<]+?>', '', msg)       # Убираем все теги HTML

        for i in msg.splitlines():
            if i.find(' родилась в ') > 0 or i.find(' родился в ') > 0:
                age = int(i[-4:])
                break

        msg = 'http://www.usynovite.ru/child/?id={0}\n'.format(anketa_id) + msg
        image = 'http://www.usynovite.ru/photos/{1}/{0}.jpg'.format(anketa_id, anketa_id[:2])

        logging.info("Год рождения - {0}".format(age))

        if select_anketa(db_old, db_new, anketa_id) == 0:
            logging.info("Анкеты {0} нет в БД".format(anketa_id))
            if age > 1900:
                telegram_send_image(image)
                if telegram_send_text(msg):
                    insert_anketa(db_new, anketa_id, age)
                    logging.info('Анкета {0} добавлена в БД'.format(anketa_id))
                else:
                    logging.info('Не записываем анкету в БД')
            else:
                insert_anketa(db_new, anketa_id, age)
                logging.info('Анкета {0} добавлена в БД'.format(anketa_id))
        else:
            insert_anketa(db_new, anketa_id, age)
            logging.info("Анкета {0} уже есть в БД".format(anketa_id))

    return count


def main():

    logging_set()
    logging.info("========== Start ==========")

    telegram_send_text("""
    Добрый день.
    Это канал в который в автоматическом режиме выкладываются новые анкеты с сайта usynovite.ru.
    Процесс поиска новых анкет запускается каждый день в 8 утра МСК.
    
    Я не имею какого-либо отношения к сайту usynovite.ru, органам опеки, департаменту государственной политики в сфере защиты прав детей. 
    По всем вопросам можно обращаться в телеграм: https://t.me/alexeytimofeew.
    """)


    db_old = db_old_connect()
    db_new = db_new_connect()

    count = 1

    multipart_data = MultipartEncoder(
        fields={'region': '1,2,22,28,29,30,3,31,32,4,33,34,35,36,5,80,75,85,37,19,83,38,6,39,40,41,84,8,9,42,43,10'
                          ',44,23,24,91,45,46,47,48,49,11,12,77,50,51,82,52,53,54,55,56,57,58,59,25,60,7,15,61,62,'
                          '63,78,64,21,65,66,90,13,67,26,68,14,69,70,71,72,16,73,27,17,88,74,18,20,79,89,76',
                'sex': '',
                'adobtion': '',
                'year': '',
                'family': '',
                'month': '',
                'names': '',
                'personal_data': '1'})

    s = requests.session()
    r = s.post('http://www.usynovite.ru/db/', data=multipart_data,
               headers={'Content-Type': multipart_data.content_type})
    html = r.text
    count = parser(html, db_new, db_old, count)

    end = 1
    while end > 0:
        r = s.get("http://www.usynovite.ru/db/?p={0}&last-search".format(str(end+1)))
        if (len(r.content) > 55000) and end < 6000:
            html = r.text
            count = parser(html, db_new, db_old, count)
            end += 1
        else:
            end = 0

    db_close(db_new, db_old)

    logging.info("========== Stop ==========")


if __name__ == "__main__":
    main()
