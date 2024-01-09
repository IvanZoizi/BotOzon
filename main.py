import time
import logging

from selenium.webdriver.common.by import By
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType
from aiogram.dispatcher import FSMContext
from selenium import webdriver
from fake_useragent import UserAgent

import config
from keyboard import *
from states import UrlStates

logging.basicConfig(level=logging.ERROR, filename="errors.log")
logging.basicConfig(level=logging.INFO, filename="info.log")
storage = MemoryStorage()

bot = Bot(token=config.APIKEY)  # https://t.me/Chat_ruletka_chat_bot
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands="start")
async def start(message: types.Message):
    await message.answer("<b>👋 Приветствуем!</b>\nНаш бот поможет Вам узнать цену на товар в Ozon.\nХотите узнать цену?",
                         reply_markup=get_start_kb(), parse_mode="html")


@dp.message_handler(content_types=[ContentType.TEXT])
async def get_text(message: types.Message, state: FSMContext):
    if message.text.lower() == "💰 узнать цену на товар":
        await message.answer("✉️ <b>Введите ссылку товара на Ozon.</b>", reply_markup=types.ReplyKeyboardRemove(),
                             parse_mode="html")
        await UrlStates.url.set()
    else:
        await message.answer("👇  <b>Если вы заблудились, скорее нажимайте кнопку.</b>", reply_markup=get_start_kb(),
                             parse_mode="html")


@dp.message_handler(state=UrlStates.url)
async def get_ozon_url(message: types.Message, state: FSMContext):
    if 'https://www.ozon.ru/product/' not in message.text.lower():
        await message.answer("❌ Ошибка. Попробуйте еще раз!")
        return
    msg = await message.answer("⏳ Идет поиск, это займет пару секунд!")
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(
        f"user-agent={UserAgent.random}")
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--enable-javascript')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    try:
        driver.get(message.text)
        time.sleep(2)
        price_with_card, price_not_card = None, None
        for i in driver.find_elements(By.TAG_NAME, 'span'):
            if i.text:
                if '₽' in i.text:
                    if 'карт' in i.text.lower():
                        price_with_card = i.text.split('\n')[0]
                    else:
                        if price_with_card:
                            if i.text.split() != price_with_card.split():
                                price_not_card = i.text
                if price_not_card and price_with_card:
                    break
        await msg.delete()
        await message.answer(f"💳 Цена с картой - <b>{price_with_card}</b>\n"
                             f"💵 Цена без карты - <b>{price_not_card}</b>", reply_markup=get_start_kb(), parse_mode="html")
        await state.finish()
    except Exception as ex:
        print(ex)
        logging.error(ex)
        await msg.delete()
        await message.answer("❌ Ошибка. Попробуйте чуть позже!", reply_markup=get_start_kb())
        await state.finish()
    finally:
        driver.close()
        driver.quit()

if __name__ == '__main__':
    executor.start_polling(dp)
