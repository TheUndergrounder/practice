import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram import F
from aiogram import html
#from config_reader import config
from raspisanie import *

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7265948579:AAGRZ1rwfn19i9KUYzukR7U8M5WfEoXT1ko")
# Диспетчер
dp = Dispatcher()


mode = "normal"
address = ''
day = ''
teachers_fio = ''
audience=''
def update_day():
    global day
    try:
        url = "https://guap.ru/rasp/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        day=soup.find('em').text[2:]
        print(f"День обновлен: {day}")
    except Exception as e:
        print(f"Ошибка при обновлении дня: {e}")
def run_scheduler():
    schedule.every().day.at("00:00").do(update_day)
    while True:
        schedule.run_pending()
        time.sleep(1)
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
def get_back_keyboard(mesage:str=''):
    kb = [
        [types.KeyboardButton(text="Назад")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=mesage+" или нажмите 'Назад'"*(mesage!='')
    )
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Расписание", reply_markup=get_main_keyboard())

@dp.message(F.text.lower() == "преподаватели")
async def cmd_prep(message: types.Message):
    global mode
    mode = "teacher"
    await message.reply("Введите фамилию преподавателя", reply_markup=get_back_keyboard('Введите фамилию преподавателя'))
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
            types.KeyboardButton(text="Назад"),
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите адрес или нажмите 'Назад'"
    )
    await message.reply("Выберите адрес", reply_markup=keyboard)

@dp.message(F.text.lower() == "гастелло 15")
async def cmd_gastello(message: types.Message):
    global mode, address
    mode = "auditorium"
    address = "Гастелло 15"
    await message.reply("Введите номер аудитории", reply_markup=get_back_keyboard())

@dp.message(F.text.lower() == "ленсовета 14")
async def cmd_lensoveta(message: types.Message):
    global mode, address
    mode = "auditorium"
    address = "Ленсовета 14"
    await message.reply("Введите номер аудитории", reply_markup=get_back_keyboard())

@dp.message(F.text.lower() == "б. морская 67")
async def cmd_bm(message: types.Message):
    global mode, address
    mode = "auditorium"
    address = "Б. Морская 67"
    await message.reply("Введите номер аудитории", reply_markup=get_back_keyboard())

@dp.message(F.text.lower() == "показать полное расписание")
async def show_full_schedule(message: types.Message):
    if mode=='full_schedule_prep':
        title = "Расписание преподавателя <b><u>" + teachers_fio + "</u></b>\n"
        reply = title+get_rasp(teachers_fio)
        await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())
    elif mode=='full_schedule_audit':
        title = "Расписание <b><u>" + audience + "</u></b>\n"
        reply = title + get_rasp_audit(address, audience)
        print(len(reply))
        print(reply)
        if len(reply)>4095:
            half=reply.find('<i>Четверг')
            await message.reply(reply[:half], parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())
            await message.reply(reply[half:], parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())
        else:
            await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())
@dp.message(F.text)
async def choose_prep(message: types.Message):
    global mode, day, teachers_fio, audience
    if mode == "teacher":
        teacher = get_name(message.text)
        if teacher == "":
            await message.reply("Такой преподаватель не найден")
        else:
            title = "Расписание преподавателя на сегодня <b><u>" + teacher + "</u></b>\n"
            reply = get_rasp(teacher, day)
            if reply=='':
                reply='Сегодня выходной!!'+'🥳'
            else:
                reply=title+reply
            kb = [
                [types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="Показать полное расписание")
                 ]
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder='Выберите "полное расписание" или "назад"'
            )
            mode='full_schedule_prep'
            teachers_fio=teacher
            await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    elif mode == 'auditorium' or mode=='full_schedule_audit':
        title = "Расписание <b><u>" + message.text + "</u></b> на сегодня\n"
        reply = get_rasp_audit(korpus=address, audience=message.text, today=day)
        if reply == '':
            reply = 'такой аудитории не найдено'
            await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())
        else:
            reply = title + reply
            kb = [
                [types.KeyboardButton(text="Назад"),
                 types.KeyboardButton(text="Показать полное расписание")
                 ]
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder='Выберите "полное расписание" или "назад"'
            )
            audience=message.text
            mode="full_schedule_audit"
            await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await message.reply("Неизвестная команда")

async def main():
    threading.Thread(target=run_scheduler).start()
    update_day()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())