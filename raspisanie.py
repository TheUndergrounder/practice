from json import *
import schedule
import time
import requests
from bs4 import BeautifulSoup
import threading
f = open("shcedule.json", encoding="utf8")
schedule_prep = load(f)
schedule_audit=load(open("shcedule_of_audiences.json", encoding="utf8"))
def get_name(message):
    global schedule_prep
    teachers=schedule_prep.keys()
    for teacher in teachers:
        if teacher.lower().startswith(message.lower()):
            return teacher
    return ""
days_of_week={'Понедельник':'Пн', 'Вторник':'Вт', 'Среда':'Ср', 'Четверг':'Чт', 'Пятница':'Пт', 'Суббота':'Сб'}
def get_rasp(teacher, today=None):
    global schedule_prep
    text=""
    if not(today):
        curr_day_of_week='Понедельник'
        flag=1
        for para, tema in schedule_prep[teacher].items():
            key_of_para=para.split()
            if (key_of_para[0] == curr_day_of_week) and flag:
                text += '<b><i>' + days_of_week[curr_day_of_week] + '</i></b>\n'
            if key_of_para[0] != curr_day_of_week:
                curr_day_of_week = key_of_para[0]
                text += '\n<b><i>' + days_of_week[curr_day_of_week] + '</i></b>\n'
            flag=0
            text+='🔺' if key_of_para[4] == 'верхняя' else '🔽'
            text += "<b>"+' '.join(key_of_para[1:])+"</b>\n<i>"
            for num,i in enumerate(tema):
                if type(i) is str:
                    text += i
                else:
                    text += 'Групп' + ("а: " if len(i) == 1 else 'ы: ')
                    text += " ".join(i) + " "
                text += ';' * (num > 0) + ' '*(num > 0 and num!=3)
            text += "</i>\n"
    else:
        today = today.split(',')
        day_of_week = (today[0]).capitalize()
        up_or_down = today[2][1:].split()[0]
        flag = 1
        for para, tema in schedule_prep[teacher].items():
            key_of_para = para.split()
            if key_of_para[0] == day_of_week and key_of_para[4] == up_or_down:
                text += ('<b><i>' + days_of_week[day_of_week] + " " + (
                    '🔺' if up_or_down == 'верхняя' else '🔽') + up_or_down + '</i></b>\n') * (flag)
                flag = 0
                todays_para = para.split()[1:4]
                text += "<b>" + ' '.join(todays_para) + "</b>\n"
                text += "<i>"
                for num,i in enumerate(tema):
                    if type(i) is str:
                        text += i
                    else:
                        text += ' Групп' + ("а: " if len(i) == 1 else 'ы: ')
                        text += " ".join(i) + " "
                    text += ';' * (num > 0) + ' '*(num > 0 and num!=3)
                text += "</i>\n"
    return text
def get_rasp_audit(korpus:str, audience:str, today=None):
    global schedule_audit
    text = ""
    try:
        if not (today):
            curr_day_of_week = 'Понедельник'
            flag = 1
            for para, tema in schedule_audit[korpus][audience].items():
                key_of_para = para.split()
                if (key_of_para[0] == curr_day_of_week) and flag:
                    text += '<b><i>' + days_of_week[curr_day_of_week] + '</i></b>\n'
                if key_of_para[0] != curr_day_of_week:
                    curr_day_of_week = key_of_para[0]
                    text += '\n<b><i>' + days_of_week[curr_day_of_week] + '</i></b>\n'
                flag = 0
                text += '🔺' if key_of_para[4] == 'верхняя' else '🔽'
                text += "<b>" + ' '.join(key_of_para[1:5]) + "</b>\n<i>"
                for num, i in enumerate(tema):
                    if type(i) is str:
                        text += (i if num != 1 else i[:-1])
                    else:
                        text += 'Групп' + ("а: " if len(i) == 1 else 'ы: ')
                        for n, group in enumerate(i):
                            text += group + (' ' * (n != (len(i) - 1)))
                    text += ';' * (num > 0) + ' '*(num > 0 and num!=3)
                text += "</i>\n"
        else:
            today = today.split(',')
            day_of_week = (today[0]).capitalize()
            up_or_down = today[2][1:].split()[0]
            flag=1
            for para, tema in schedule_audit[korpus][audience].items():
                key_of_para = para.split()
                if key_of_para[0] == day_of_week and key_of_para[4] == up_or_down:
                    text += ('<b><i>' + days_of_week[day_of_week] + " " + ('🔺' if up_or_down == 'верхняя' else '🔽') +
                             up_or_down+'</i></b>\n') * flag
                    flag = 0
                    todays_para = para.split()[1:4]
                    text += "<b>" + ' '.join(todays_para) + "</b>\n"
                    text += "<i>"
                    for num, i in enumerate(tema):
                        if type(i) is str:
                            text += i
                        else:
                            text += 'Групп' + ("а: " if len(i) == 1 else 'ы: ')
                            for n, group in enumerate(i):
                                text += group + ' '*(n == (len(i)-1))
                        text += ';' * (num > 0) + ' '*(num > 0 and num!=3)
                    text += "</i>\n"
            if text == '':
                return 'Сегодня у аудитории выходной'
        return text
    except:
        return ""
def load_teachers():
    with open('teachers_from_14.txt', 'r', encoding='1251') as file:
        return file.read().split('\n')
teachers_list = load_teachers()
def search_teachers(query):
    if query:
        return [teacher for teacher in teachers_list if teacher.lower().startswith(query.lower())]
    else:
        return teachers_list