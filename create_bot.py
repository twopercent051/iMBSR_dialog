import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
#from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from tgbot.config import load_config


config = load_config(".env")
storage = MemoryStorage()  # RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()

logger = logging.getLogger(__name__)
file_log = logging.FileHandler("logger.log")
console_out = logging.StreamHandler()
logging.basicConfig(handlers=(file_log, console_out), level=logging.INFO)
