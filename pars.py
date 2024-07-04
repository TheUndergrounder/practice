import requests
link="https://guap.ru/rasp/"
responce=requests.get(link).text
print(responce)