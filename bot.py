import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from aiogram import html
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
teachers_list = load_teachers()

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
            InlineKeyboardButton(text="Преподаватели", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="Аудитории", callback_data="auditoriums")
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb), ReplyKeyboardRemove()
def get_back_keyboard(message:str=''):
    kb = [[KeyboardButton(text="Назад")]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=message+" или нажмите 'Назад'"*(message!='')
    )

@dp.inline_query()
async def inline_query_handler(query: InlineQuery):
    if len(query.query)<1:
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
    keyboard, remove_keyboard = get_main_keyboard()
    await message.answer("Выберите действие", reply_markup=remove_keyboard)
    await message.answer("Главная страница", reply_markup=keyboard)



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
    keyboard, remove_keyboard = get_main_keyboard()
    await message.answer("Выберите действие", reply_markup=remove_keyboard)
    await message.answer("Главная страница", reply_markup=keyboard)

@dp.callback_query(F.data == "auditoriums")
async def process_auditoriums(callback_query: types.CallbackQuery):
    kb = [
        [
            InlineKeyboardButton(text="Гастелло 15", callback_data="address:Гастелло 15"),
            InlineKeyboardButton(text="Ленсовета 14", callback_data="address:Ленсовета 14"),
        ],
        [
            InlineKeyboardButton(text="Б. Морская 67", callback_data="address:Б. Морская 67"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await callback_query.message.edit_text("Выберите адрес", reply_markup=keyboard)
    await callback_query.answer()
@dp.callback_query(F.data.startswith("address:"))
async def process_address(callback_query: types.CallbackQuery):
    global mode, address
    mode = "auditorium"
    address = callback_query.data.split(":")[1]
    await callback_query.message.edit_text(f"Введите номер аудитории для {address}")
    await callback_query.answer()

@dp.message(F.text.lower() == "показать полное расписание")
async def show_full_schedule(message: types.Message):
    if mode=='full_schedule_prep':
        title = "Расписание преподавателя <b><u>" + teachers_fio + "</u></b>\n"
        reply = title+get_rasp(teachers_fio)
        await message.reply(reply, parse_mode=ParseMode.HTML, reply_markup=get_back_keyboard())
    elif mode=='full_schedule_audit':
        title = "Расписание <b><u>" + audience + "</u></b>\n"
        reply = title + get_rasp_audit(address, audience)
        if len(reply)>4095:
            half=reply.find('<b><i>Чт')
            print(reply, len(reply), len(reply[:half]), len(reply[half:]))
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
        [KeyboardButton(text="Назад"),
         KeyboardButton(text="Показать полное расписание")]
    ]
    keyboard = ReplyKeyboardMarkup(
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
            reply = 'Аудитории, к сожалению, не существует'
            await message.answer_sticker(r'CAACAgIAAxkBAAEG6b5mlTydqVqKBzx6ucCpoTEtn_2DWwACMgADlb9JMp-D9IETtGgoNQQ')
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
    await bot.delete_webhook(drop_pending_updates=True)

    bot_info = await bot.get_me()
    print(f"Бот запущен. Username: @{bot_info.username}")

    # Запускаем поллинг с игнорированием ожидающих обновлений
    await dp.start_polling(bot, drop_pending_updates=True)

if __name__ == "__main__":
    asyncio.run(main())