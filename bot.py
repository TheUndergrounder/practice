import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from base import *
#from config_reader import config

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

@dp.message(F.text.lower() == "преподаватели")
async def cmd_prep(message: types.Message):
    await message.reply("Выберите преподавателя\n"+list_prep())

@dp.message(F.text.lower() == "аудитории")
async def cmd_audit(message: types.Message):
    await message.reply("Расписание аудиторий")
    
# Хэндлер на команду /test1
@dp.message(Command("test1"))
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())