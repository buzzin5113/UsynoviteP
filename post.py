from bs4 import BeautifulSoup
import logging
import postgresql
import re
import requests
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
        bot.sendMessage(secret.chat_id, text=msg,  parse_mode=telegram.ParseMode.HTML)
        time.sleep(1)  # Чтобы не попасть в спам
        return True
    except telegram.TelegramError:
        logging.error('Ошибка отправки текстового сообщения в телеграм')
        return False


def telegram_send_image(url):
    """
    Send a image from url to a telegram user specified on chatId
    chat_id must be a number!
    """

    bot = telegram.Bot(secret.token)
    try:
        bot.send_photo(secret.chat_id, photo=url)
        time.sleep(1)
        return True
    except telegram.TelegramError:
        logging.error('Ошибка отправки изображения в телеграм')
        msg = "Фотография не найдена"
        telegram_send_text(msg)
        return False


def select_anketa(db, anketa_id):
    """
    Проверка наличия в БД номера анкеты
    """

    query = 'SELECT trim(number) FROM anketa WHERE number = \'{0}\''.format(anketa_id)
    select = db.prepare(query)
    return 1 if select() else 0


def insert_anketa(db, anketa_id):
    """
    Вставка номера анкеты в БД
    """

    query = 'INSERT into anketa (number) values (\'{0}\')'.format(anketa_id)
    insert = db.prepare(query)
    insert()
    logging.info("Анкета {0} добавлена в БД".format(anketa_id))


def logging_set():
    """
    Настройка логгирования
    """
    handlers = [logging.FileHandler('./post.log'), logging.StreamHandler()]
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                        level=logging.DEBUG,
                        datefmt='%Y%m%d %H%M%S',
                        handlers=handlers)


def parser(html, db, count):
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
        if select_anketa(db, anketa_id) == 0:
            logging.info("Анкеты {0} нет в БД".format(anketa_id))

            msg = re.sub('</p>', '\n', str(k))      # Из <p> делаем перевод строки
            msg = re.sub('<[^<]+?>', '', msg)       # Убираем все теги HTML

            for i in msg.splitlines():
                if i.find(' родилась в ') > 0 or i.find(' родился в ') > 0:
                    age = int(i[-4:])

            msg = 'http://www.usynovite.ru/child/?id={0}\n'.format(anketa_id) + msg
            image = 'http://www.usynovite.ru/photos/{1}/{0}.jpg'.format(anketa_id, anketa_id[:2])

            if age > 2011:
                telegram_send_image(image)
                if telegram_send_text(msg):
                    insert_anketa(db, anketa_id)
                else:
                    logging.info('Не записываем анкету в БД')
            else:
                logging.info("Год рождения - {0}".format(age))
                insert_anketa(db, anketa_id)

        else:
            logging.info("Анкета {0} уже есть в БД".format(anketa_id))

    return count


def main():

    logging_set()
    logging.info("========== Старт ==========")

    db = postgresql.open(secret.db)

    count = 1
    count_new = 0

    payload = {'region': '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32, \
               33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65, \
               66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91',
               'sex': '',
               'adobtion': '',
               'year': '',
               'family': '',
               'month': '',
               'names': '',
               'personal_data': '1'}

    s = requests.session()
    r = s.post("http://www.usynovite.ru/db/", data=payload)
    html = r.text
    count = parser(html, db, count)

    end = 1
    while end > 0:
        r = s.get("http://www.usynovite.ru/db/?p={0}&last-search".format(str(end+1)))
        if (len(r.content) > 55000) and end < 6000:
            html = r.text
            count = parser(html, db, count)
            end += 1
        else:
            end = 0

    db.close()

    logging.info("========== Стоп ==========")


if __name__ == "__main__":
    main()

