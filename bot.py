import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram import F
from aiogram import html
from base import *
#from config_reader import config
from raspisanie import *
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7265948579:AAGRZ1rwfn19i9KUYzukR7U8M5WfEoXT1ko")
# Диспетчер
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Преподаватели"),
            types.KeyboardButton(text="Аудитории")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )
    await message.answer("Расписание", reply_markup=keyboard)

mode="normal"
@dp.message(F.text.lower() == "преподаватели")
async def cmd_prep(message: types.Message):
    global mode
    mode="teacher"
    await message.reply("Введите фамилию преподавателя")

@dp.message(F.text.lower() == "аудитории")
async def cmd_audit(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Гастелло"),
            types.KeyboardButton(text="Ленсовета"),
            types.KeyboardButton(text="Большая Морская"),
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


# Хэндлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

@dp.message(F.text)
async def read_message(message: types.Message):
    global mode
    if mode=="teacher":
        mode="normal"
        teacher=get_name(message.text)
        if teacher=="":
            await message.reply("Такой преподаватель не найден")
        else:
            reply="Расписание преподавателя <b><u>" + teacher+"</u></b>\n"
            """for string in get_rasp(teacher):
                string=string.replace("День недели:", "<b>📆")
                string = string.replace(", Чётность недели: ", "</b>\n")
                string = string.replace(", Номер пары: ", "\n▼")
                string = string.replace(": Тип пары:", "\n")
                string = string.replace(", Предмет:", "")
                string = string.replace(", Аудитория: – ", "\n")
                string = string.replace("[", "")
                string = string.replace("]", "")
                string = string.replace("\'", "")
                
                reply+="\n"+string
                """
            reply+=get_rasp(teacher)
            await message.reply(reply,parse_mode=ParseMode.HTML)
    else:
        await message.reply("Неизвестная команда")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())