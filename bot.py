import asyncio
import logging
import os

from aiogram import filters
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ContentType
from typing import Any

from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user, calendarDialog, calendar_start
from tgbot.handlers.echo import register_echo
from tgbot.handlers.testing import register_testing
from tgbot.middlewares.environment import EnvironmentMiddleware
from tgbot.misc.scheduler import scheduler_jobs
from tgbot.models.sql_connector import sql_start, close_sql

from create_bot import bot, dp, config, scheduler, logger

from aiogram_dialog import (
    Dialog, DialogManager, DialogRegistry,
    ChatEvent, StartMode, Window,
)
from aiogram_dialog.exceptions import UnknownIntent
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.kbd import Calendar
from datetime import datetime, date

src_dir = os.path.normpath(os.path.join(__file__, os.path.pardir))


# class DialogSG(StatesGroup):
#     greeting = State()
#     age = State()
#     finish = State()
#
#
# async def get_data(dialog_manager: DialogManager, **kwargs):
#     age = dialog_manager.data.get("age", None)
#     return {
#         "name": dialog_manager.data.get("name", ""),
#         "age": age,
#         "can_smoke": age in ("18-25", "25-40", "40+"),
#     }
#
#
# async def name_handler(message: Message, message_input: MessageInput,
#                        manager: DialogManager):
#     if manager.is_preview():
#         await manager.next()
#         return
#     manager.data["name"] = message.text
#     await message.answer(f"Nice to meet you, {message.text}")
#     await manager.next()
#
#
# async def other_type_handler(message: Message, message_input: MessageInput,
#                              manager: DialogManager):
#     await message.answer("Text is expected")
#
#
# async def on_finish(callback: CallbackQuery, button: Button,
#                     manager: DialogManager):
#     if manager.is_preview():
#         await manager.done()
#         return
#     await callback.message.answer("Thank you. To start again click /start")
#     await manager.done()
#
#
# async def on_age_changed(callback: ChatEvent, select: Any,
#                          manager: DialogManager,
#                          item_id: str):
#     manager.data["age"] = item_id
#     await manager.next()
#
#
# async def on_date_sel(c: CallbackQuery, widget, manager: DialogManager, selected_date: date):
#     # await cal.process_callback(c, widget, manager)
#     print("Date: " + str(selected_date))
#     await c.message.answer(str(selected_date))
#
# dialog = Dialog(
#     Window(
#         Const("Greetings! Please, introduce yourself:"),
#         #StaticMedia(
#         #    path=os.path.join(src_dir, "python_logo.png"),
#         #    type=ContentType.PHOTO,
#         #),
#         # MessageInput(name_handler, content_types=[ContentType.TEXT]),
#         Calendar(id='calendar_', on_click=on_date_sel),
#         state=DialogSG.greeting,
#     ),
#     Window(
#         Format("{name}! How old are you?"),
#         Select(
#             Format("{item}"),
#             items=["0-12", "12-18", "18-25", "25-40", "40+"],
#             item_id_getter=lambda x: x,
#             id="w_age",
#             on_click=on_age_changed,
#         ),
#         state=DialogSG.age,
#         getter=get_data,
#         preview_data={"name": "Tishka17"}
#     ),
#     Window(
#         Multi(
#             Format("{name}! Thank you for your answers."),
#             Const("Hope you are not smoking", when="can_smoke"),
#             sep="\n\n",
#         ),
#         Row(
#             Back(),
#             SwitchTo(Const("Restart"), id="restart", state=DialogSG.greeting),
#             Button(Const("Finish"), on_click=on_finish, id="finish"),
#         ),
#         getter=get_data,
#         state=DialogSG.finish,
#     )
# )
#
#
# async def start_d(message: Message, dialog_manager: DialogManager):
#     # it is important to reset stack because user wants to restart everything
#     await dialog_manager.start(DialogSG.greeting, mode=StartMode.RESET_STACK)
#
#
# async def error_handler_d(event, dialog_manager: DialogManager):
#     """Example of handling UnknownIntent Error and starting new dialog"""
#     if isinstance(event.exception, UnknownIntent):
#         await dialog_manager.start(DialogSG.greeting,
#                                    mode=StartMode.RESET_STACK)
#     else:
#         return UNHANDLED
#
#
# def new_registry(dp):
#     registry = DialogRegistry(dp)
#     registry.register(dialog)
#     return registry


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)
    register_testing(dp)
    # register_echo(dp)


async def main():

    logger.info("Starting bot")

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)
    await sql_start()

    logger.info("SQL initialized")

    registry = DialogRegistry(dp)
    registry.register(calendarDialog)
    dp.register_callback_query_handler(calendar_start, lambda x: x.data == 'calendar_start', state="*")

    await scheduler_jobs()
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
        scheduler.shutdown(True)
        await close_sql()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
