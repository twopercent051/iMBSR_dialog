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


def deleter():
    host = config.db.host
    user = config.db.user
    password = config.db.password
    db_name = config.db.database
    connection = connection_init(host, user, password, db_name)
    try:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE tests')
            cursor.execute('DROP TABLE users')
            # # cursor.execute('DROP TABLE texts')
            # cursor.execute('DROP TABLE practices')
    finally:
        connection.close()


def corrector():
    host = config.db.host
    user = config.db.user
    password = config.db.password
    db_name = config.db.database
    connection = connection_init(host, user, password, db_name)
    sql_query = 'UPDATE users SET week_id = %s, next_step_time = %s, next_step_name = %s, day = %s WHERE user_id = %s'
    sql_tuple = (6, int(time.time()), 'week_6:remind_daily', 7, 389929933)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query, sql_tuple)
    finally:
        connection.commit()
        connection.close()


deleter()
# corrector()
