import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram import F
from aiogram import html
#from config_reader import config
from raspisanie import *
import re

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7265948579:AAGRZ1rwfn19i9KUYzukR7U8M5WfEoXT1ko")
# Диспетчер
dp = Dispatcher()


mode = "normal"
address = ''
def get_main_keyboard():
    kb = [
        [
            types.KeyboardButton(text="Преподаватели"),
            types.KeyboardButton(text="Аудитории")
        ],
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Расписание", reply_markup=get_main_keyboard())

@dp.message(F.text.lower() == "преподаватели")
async def cmd_prep(message: types.Message):
    global mode
    mode = "teacher"
    kb = [
        [types.KeyboardButton(text="Назад")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Введите фамилию преподавателя или нажмите 'Назад'"
    )
    await message.reply("Введите фамилию преподавателя", reply_markup=keyboard)
@dp.message(F.text.lower() == "назад")
async def cmd_back(message: types.Message):
    global mode
    mode = "normal"
    await message.reply("Выберите действие", reply_markup=get_main_keyboard())

@dp.message(F.text.lower() == "аудитории")
async def cmd_audit(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Гастелло 15"),
            types.KeyboardButton(text="Ленсовета 14"),
            types.KeyboardButton(text="Б. Морская 67"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите адрес"
    )
    await message.reply("Выберите адрес", reply_markup=keyboard)

@dp.message(F.text.lower() == "гастелло")
async def cmd_gastello(message: types.Message):
    global mode, address
    mode = "auditorium"
    address = "Гастелло"
    await message.reply("Введите номер аудитории или первые 2 цифры номера")

@dp.message(F.text.lower() == "ленсовета")
async def cmd_lensoveta(message: types.Message):
    global mode, address
    mode = "auditorium"
    address = "Ленсовета"
    await message.reply("Введите номер аудитории или первые 2 цифры номера")

@dp.message(F.text.lower() == "большая морская")
async def cmd_bm(message: types.Message):
    global mode, address
    mode = "auditorium"
    address = "Большая Морская"
    await message.reply("Введите номер аудитории или первые 2 цифры номера")


@dp.message(F.text)
async def read_message(message: types.Message):
    global mode
    if mode == "teacher":
        if message.text.lower() != "назад":
            teacher = get_name(message.text)
            if teacher == "":
                await message.reply("Такой преподаватель не найден")
            else:
                reply = "Расписание преподавателя <b><u>" + teacher + "</u></b>\n"
                reply += get_rasp(teacher)
                await message.reply(reply, parse_mode=ParseMode.HTML)
    else:
        await message.reply("Неизвестная команда")

async def main():
    threading.Thread(target=run_scheduler).start()
    update_day()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())