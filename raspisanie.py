from json import *
import schedule
import time
import requests
from bs4 import BeautifulSoup
import threading
def get_name(message):
    f = open("shcedule.json", encoding="utf8")
    shcedule = load(f)
    teachers=shcedule.keys()
    for teacher in teachers:
        if message.lower() in teacher.lower():
            return teacher
    return ""
def get_rasp(teacher):
    f=open("shcedule.json", encoding="utf8")
    shcedule=load(f)
    text=""
    for para,tema in shcedule[teacher].items():
        text+="<i>"+para+"</i>\n"
        for i in tema:
            if type(i) is str:
                text+="<b>"+i+"</b> "
            else:
                text+=" ".join(i)+" "
        text+="\n"
    return text

day=''
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