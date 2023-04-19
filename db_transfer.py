import pymysql
from create_bot import config
import time


def connection_init(host, user, password, db_name):
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def transfer():
    host = config.db.host
    user = config.db.user
    password = config.db.password
    db_name = config.db.database
    connection = connection_init(host, user, password, db_name)
    sql_query = 'SELECT * FROM texts;'
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            texts = cursor.fetchall()
        return texts
    finally:
        connection.commit()
        connection.close()


def new_db():
    texts = transfer()

    connection = connection_init(host, user, password, db_name)
    query = 'INSERT INTO texts (task, remind_meditation, remind_other, remind_daily, other) VALUES (%s, %s, %s, %s, %s);'
    try:
        for text in texts:
            data = (text['task'], text['remind_meditation'], text['remind_other'], text['remind_daily'], text['other'])
            with connection.cursor() as cursor:
                cursor.execute(query, data)
    finally:
        connection.commit()
        connection.close()


new_db()
