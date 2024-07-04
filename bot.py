import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
#from config_reader import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7265948579:AAGRZ1rwfn19i9KUYzukR7U8M5WfEoXT1ko")
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

# Хэндлер на команду /test1
@dp.message(Command("prep"))
async def cmd_test1(message: types.Message):
    await message.reply("Shahomyr zanyat")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())