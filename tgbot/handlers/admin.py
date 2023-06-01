import os

from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.admin_inline import *
from tgbot.models.sql_connector import *
from tgbot.misc.states import FSMAdmin
from tgbot.misc.list_creator import create_csv, failed_mail_csv
from create_bot import bot, config, logger

admin_group = config.misc.admin_group


async def admin_start_msg(message: Message):
    text = 'Главное меню'
    kb = menu_kb()
    await FSMAdmin.home.set()
    await message.answer(text, reply_markup=kb)


async def admin_start_clb(callback: CallbackQuery):
    text = 'Главное меню'
    kb = menu_kb()
    await FSMAdmin.home.set()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


async def mailing_start(callback: CallbackQuery):
    text = [
        'Введите сообщение. Оно будет отправлено всем зарегистрированным пользователям. Допустимые форматы:',
        '✅ Текст',
        '✅ Фото',
        '✅ Видео',
        '✅ Видео-кружок'
    ]
    kb = home_kb()
    await FSMAdmin.mailing.set()
    await callback.message.answer('\n'.join(text), reply_markup=kb)
    await bot.answer_callback_query(callback.id)


async def mailing_finish(message: Message):
    user_list = await get_users_sql()
    counter = 0
    users_failed = []
    for user in user_list:
        user_id = user['user_id']
        try:
            if message.content_type == 'text':
                await bot.send_message(user_id, message.text)
            if message.content_type == 'photo':
                photo = message.photo[0].file_id
                text = message.caption
                await bot.send_photo(user_id, photo, text)
            if message.content_type == 'video':
                video = message.video.file_id
                text = message.caption
                await bot.send_video(user_id, video, caption=text)
            if message.content_type == 'video_note':
                video = message.video_note.file_id
                await bot.send_video_note(user_id, video)
            counter += 1
        except Exception as ex:
            print(ex)
            username = user['username']
            if username is None:
                username = 'USERNAME IS NONE'
            else:
                username = '@' + username
            users_failed.append(username)
    if len(users_failed) != 0:
        await failed_mail_csv(users_failed)
        doc_path = f'{os.getcwd()}/fail_users.csv'
        # await bot.send_document(chat_id=admin_group, document=open(doc_path, 'rb'))

    text = f'Сообщение разослали {counter} пользователей из {len(user_list)}'
    kb = home_kb()
    await FSMAdmin.home.set()
    await message.answer(text, reply_markup=kb)


async def metrics(callback: CallbackQuery):
    await create_csv()
    doc_path = f'{os.getcwd()}/users.csv'
    await bot.send_document(chat_id=admin_group, document=open(doc_path, 'rb'))
    await bot.answer_callback_query(callback.id)


async def edition(callback: CallbackQuery):
    text = 'Выберите неделю для редактирования'
    kb = edition_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


async def edit_week(callback: CallbackQuery):
    week_id = int(callback.data.split(':')[1])
    text = 'Выберите текст для редактуры'
    kb = week_kb(week_id)
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


async def edit_text_start(callback: CallbackQuery, state: FSMContext):
    week_id = int(callback.data.split(':')[1].split('_')[1])
    title = callback.data.split(':')[2]
    week_profile = await get_text_sql(week_id)
    value = week_profile[title]

    kb = home_kb()
    if value is None:
        text = 'Пустое значение. Введите сообщение, чтобы сохранить его в БД'
        await callback.message.answer(text, reply_markup=kb)
    else:
        if week_id == 1 and title == 'other':
            try:
                await bot.send_video_note(admin_group, video_note=value, reply_markup=kb)
            except:
                await callback.message.answer(value, reply_markup=kb)
        else:
            text = value
            await callback.message.answer(text, reply_markup=kb)
    async with state.proxy() as data:
        data['week_id'] = week_id
        data['title'] = title
    await FSMAdmin.edit.set()
    await bot.answer_callback_query(callback.id)


async def edit_text_finish(message: Message, state: FSMContext):
    text = 'Сообщение обновлено'
    kb = home_kb()
    async with state.proxy() as data:
        week_id = data.as_dict()['week_id']
        title = data.as_dict()['title']
    logger.info(f'week:{week_id} || title:{title}')
    if week_id == 1 and title == 'other':
        new_text = message.video_note.file_id
    else:
        new_text = message.html_text
    await FSMAdmin.home.set()
    await edit_text_sql(week_id, title, new_text)
    await message.answer(text, reply_markup=kb)


async def support_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split(':')[1]
    text = 'Введите текст ответа'
    kb = home_kb()
    async with state.proxy() as data:
        data['user_id'] = user_id
    await FSMAdmin.support.set()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)


async def support_finish(message: Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = data.as_dict()['user_id']
    await bot.send_message(user_id, message.text)
    text = 'Ответ отправлен'
    kb = home_kb()
    await FSMAdmin.home.set()
    await message.answer(text, reply_markup=kb)


def register_admin(dp: Dispatcher):
    mail_types = ['text', 'photo', 'video', 'video_note']

    dp.register_message_handler(admin_start_msg, commands=["start"], state="*", chat_id=admin_group)
    dp.register_message_handler(edit_text_finish, content_types=mail_types, state=FSMAdmin.edit,
                                chat_id=admin_group)
    # dp.register_message_handler(edit_video_note, content_types='video_note', state=FSMAdmin.edit, chat_id=admin_group)
    dp.register_message_handler(support_finish, content_types='text', state=FSMAdmin.support, chat_id=admin_group)
    dp.register_message_handler(mailing_finish, content_types=mail_types, state=FSMAdmin.mailing, chat_id=admin_group)

    dp.register_callback_query_handler(admin_start_clb, lambda x: x.data == 'home', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(mailing_start, lambda x: x.data == 'mailing', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(metrics, lambda x: x.data == 'metrics', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(edition, lambda x: x.data == 'edition', state='*', chat_id=admin_group)
    dp.register_callback_query_handler(edit_week, lambda x: x.data.split(':')[0] == 'edit_week', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(edit_text_start, lambda x: x.data.split(':')[0] == 'edit_text', state='*',
                                       chat_id=admin_group)
    dp.register_callback_query_handler(support_start, lambda x: x.data.split(':')[0] == 'support', state='*',
                                       chat_id=admin_group)
