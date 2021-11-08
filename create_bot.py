from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import config

TOKEN = config["TOKEN"]
ADMINS = config["ADMINS"]
USERS = ["2044572933"]

# TODO СДЕЛАТЬ ХЭШТЭГИ ДЛЯ СООБЩЕНИЙ (НОВОСТЬ, ЗАЯВКА)

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)