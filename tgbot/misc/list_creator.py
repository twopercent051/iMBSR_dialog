import csv
import os
from datetime import date

from tgbot.models.sql_connector import get_users_sql, get_practices_sql


async def create_csv():
    users_list = await get_users_sql()
    with open(f'{os.getcwd()}/users.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Username',
                'Имя',
                'Город',
                'Эл. почта',
                'Ожидания',
                'Дата начала курса',
                'Текущая неделя',
                'Выполнено практик на неделе'
            )
        )
    for user in users_list:
        username = user['username']
        if username is None:
            username = 'USERNAME IS NONE'
        else:
            username = '@' + username
        if user['start_date'] is None:
            start_date = 'НЕ ВЫБРАНА'
        else:
            start_date = date.fromtimestamp(user['start_date']).strftime('%d-%m-%Y')
        if user['week_id'] == 0:
            practices = 0
        else:
            practices = await get_practices_sql(user['user_id'], user['week_id'])
        with open(f'{os.getcwd()}/users.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow(
                (
                    username,
                    user['name'],
                    user['city'],
                    user['email'],
                    user['expectations'],
                    start_date,
                    user['week_id'],
                    practices
                )
            )


async def failed_mail_csv(user_list):
    with open(f'{os.getcwd()}/fail_users.csv', 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Username',
            )
        )
    for user in user_list:
        with open(f'{os.getcwd()}/fail_users.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow(
                (
                    user,
                )
            )