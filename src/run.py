from aiogram import Dispatcher
from aiogram.utils import executor

from tests import tests
from bot import dp
from db.create_all import create_all
from handlers import client


async def on_startup(_: Dispatcher):
    # create_all()
    print('Bot started')


async def on_shutdown(_: Dispatcher):
    await dp.storage.close()
    print('Bot turned off')


if __name__ == '__main__':
    tests.run_tests()
    client.register_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
