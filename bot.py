import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
#поиск
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
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
def load_teachers():
    with open('teachers_from_14.txt', 'r', encoding='1251') as file:
        return file.read().split('\n')

teachers_list = load_teachers()
def search_teachers(query):
    return [teacher for teacher in teachers_list if teacher.lower().startswith(query.lower())]

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
        input_field_placeholder="Выберите тип расписания"
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
@dp.inline_query()
async def inline_query_handler(query: InlineQuery):
    if len(query.query) < 1:
        return

    results = []
    matching_teachers = search_teachers(query.query)

    for i, teacher in enumerate(matching_teachers[:50]):  # Ограничиваем до 50 результатов
        results.append(InlineQueryResultArticle(
            id=str(i),
            title=teacher,
            input_message_content=InputTextMessageContent(
                message_text=f"Показать расписание для преподавателя: {teacher}"
            )
        ))

    await query.answer(results, cache_time=1)

@dp.message(F.text.startswith("Показать расписание для преподавателя:"))
async def handle_inline_result(message: types.Message):
    teacher = message.text.split(":")[1].strip()
    await show_teacher_schedule(message, teacher)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Главная страница", reply_markup=get_main_keyboard())


@dp.message(F.text.lower() == "преподаватели")
async def cmd_prep(message: types.Message):
    global mode
    mode = "teacher"
    bot_username = await bot.get_me()
    inline_button = InlineKeyboardButton(
        text="Начать поиск преподавателя",
        switch_inline_query_current_chat=""
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[inline_button]])

    await message.reply(
        "Нажмите на кнопку ниже, чтобы начать поиск преподавателя:",
        reply_markup=keyboard
    )
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
@dp.callback_query(lambda c: c.data and c.data.startswith('teacher:'))
async def process_callback_teacher(callback_query: types.CallbackQuery):
    await callback_query.answer()
    teacher = callback_query.data.split(':')[1]
    await show_teacher_schedule(callback_query.message, teacher)
async def show_teacher_schedule(message: types.Message, teacher: str):
    global mode, teachers_fio
    title = f"Расписание преподавателя на сегодня <b><u>{teacher}</u></b>\n"
    reply = get_rasp(teacher, day)
    if reply == '':
        reply = 'Сегодня выходной!!' + '🥳'
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
    mode = 'full_schedule_prep'
    teachers_fio = teacher
    await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=keyboard)
@dp.message(F.text)
async def choose_prep(message: types.Message):
    global mode, day, teachers_fio, audience
    if mode == "teacher":
        matching_teachers = search_teachers(message.text)
        if not matching_teachers:
            await message.reply("Преподаватель не найден. Попробуйте ввести другую часть фамилии.")
        elif len(matching_teachers) == 1:
            await show_teacher_schedule(message, matching_teachers[0])
        else:
            builder = InlineKeyboardBuilder()
            for teacher in matching_teachers[:10]:  # Ограничиваем список 10 преподавателями
                builder.button(text=teacher, callback_data=f"teacher:{teacher}")
            builder.adjust(1)  # Размещаем кнопки в один столбец
            await message.reply("Выберите преподавателя из списка:", reply_markup=builder.as_markup())
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