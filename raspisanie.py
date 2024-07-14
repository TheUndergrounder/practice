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
def get_rasp(teacher, today=None):
    global schedule_prep
    text=""
    if not(today):
        for para,tema in schedule_prep[teacher].items():
            text+="<i>"+para+"</i>\n"
            for i in tema:
                if type(i) is str:
                    text+="<b>"+i+"</b> "
                else:
                    text+=" ".join(i)+" "
            text+="\n"
    else:
        today=today.split(',')
        day_of_week=(today[0]).capitalize()
        up_or_down=today[2][1:].split()[0]
        for para, tema in schedule_prep[teacher].items():
            key_of_para=para.split()
            if key_of_para[0]==day_of_week and key_of_para[4]==up_or_down:
                text += "<i>" + para + "</i>\n"
                for i in tema:
                    if type(i) is str:
                        text += "<b>" + i + "</b> "
                    else:
                        text += " ".join(i) + " "
                text += "\n"
    return text
def get_rasp_audit(korpus:str, audience:str, today=None):
    global schedule_audit
    text = ""
    if not (today):
        for para, tema in schedule_audit[korpus][audience].items():
            text += "<i>" + para + "</i>\n"
            for i in tema:
                if type(i) is str:
                    text += "<b>" + i + "</b> "
                else:
                    text += " ".join(i) + " "
            text += "\n"
    else:
        today = today.split(',')
        day_of_week = (today[0]).capitalize()
        up_or_down = today[2][1:].split()[0]
        for para, tema in schedule_audit[korpus][audience].items():
            key_of_para = para.split()
            if key_of_para[0] == day_of_week and key_of_para[4] == up_or_down:
                text += "<i>" + para + "</i>\n"
                text += "<b>"
                for i in tema:
                    if type(i) is str:
                        text += i
                    else:
                        text += " ".join(i) + " "
                text += "</b>\n"
        if text=='':
            return 'Сегодня у аудитории выходной'
    return text
def load_teachers():
    with open('teachers_from_14.txt', 'r', encoding='1251') as file:
        return file.read().split('\n')
teachers_list = load_teachers()
def search_teachers(query):
    return [teacher for teacher in teachers_list if teacher.lower().startswith(query.lower())]