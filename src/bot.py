import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from dotenv import load_dotenv

from config import ENV_FILE_PATH

load_dotenv(ENV_FILE_PATH)

storage = RedisStorage2(
    host=os.getenv('REDIS_HOST'),
    password=os.getenv('REDIS_PASSWORD'),
    port=os.getenv('REDIS_PORT', 6379)
)

bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher(bot, storage=storage)
