from json import *
import schedule
import time
import requests
from bs4 import BeautifulSoup
import threading
f = open("shcedule.json", encoding="utf8")
schedule_prep = load(f)
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