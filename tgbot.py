import platform
import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.orm import Session
from config import API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from db.models import TelegramUsers
from db.models import engine


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['get_id'], state="*")
async def get_id(message: types.Message):
    text = "your id=" + str(message.from_user.id)
    await bot.send_message(message.from_user.id, text)


@dp.message_handler(commands=['add_me_to_the_mailing_list'], state="*")
async def add_to_mailing(message: types.Message):

    user_id = message.from_user.id
    session = Session(engine)

    query = session.query(TelegramUsers).filter(TelegramUsers.telegram_id == user_id)
    user_with_this_id = query.first()
    if user_with_this_id is not None:
        session.close()
        await bot.send_message(message.from_user.id, "you are already added")
        return

    session.add(TelegramUsers(telegram_id=user_id))
    session.commit()
    session.close()
    await bot.send_message(message.from_user.id, "you are successfully added")


@dp.message_handler(state="*")
async def start(message: types.Message):
    button_get_id = KeyboardButton('/get_id')
    button_add_to_mailing = KeyboardButton('/add_me_to_the_mailing_list')
    keybord = ReplyKeyboardMarkup(resize_keyboard=True)
    keybord.add(button_get_id)
    keybord.add(button_add_to_mailing)
    await bot.send_message(message.from_user.id, "select variant", reply_markup=keybord)


if __name__ == '__main__':

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def on_shutdown():
        await bot.close()
        await storage.close()

    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)