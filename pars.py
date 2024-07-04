import requests
from bs4 import BeautifulSoup
def find_id_teachers(*, link: str):
    responce=requests.get(link).text
    soup=BeautifulSoup(responce, 'lxml')
    block_with_teachers=(soup.find_all(name='select')[1])
    block_with_teachers=(block_with_teachers.find_all('option'))[1:]
    teachers_id_from_14=[]
    with open("teachers_from_14.txt", 'r') as file:
        teachers_from_14=file.read().split('\n')
        for teachers_option_value in block_with_teachers:
            block=(str(teachers_option_value))
            start=block.find('"')
            end=block.rfind('"')
            teachers_id=block[start+1:end]
            teachers_fio=teachers_option_value.text.split()
            teachers_fio=teachers_fio[0]+' '+teachers_fio[1]
            if teachers_fio in teachers_from_14:
                block = (str(teachers_option_value))
                start = block.find('"')
                end = block.rfind('"')
                teachers_id = block[start + 1:end]
                teachers_id_from_14.append(teachers_id)
    for teacher_id in teachers_id:
        print(teacher_id)


def write_teachers_from_14_in_file(*, link: str):
    responce = requests.get(link).text
    soup = BeautifulSoup(responce, 'lxml')
    teachers = (soup.find_all(name='a', class_='fio'))
    with open("teachers_from_14.txt",  'w') as file:
        for teacher in teachers:
            teachers_fio=(teacher.text)
            if teachers_fio == 'Док Цихон Гордон Франц Эмануэль -':
                file.write('Док Цихон Г.Ф.Э.\n')
            else:
                teachers_fio = teachers_fio.split()
                surname = f'{teachers_fio[0]} {teachers_fio[1][0]}.{teachers_fio[2][0]}.\n'
                file.write(surname)
def main():
    #write_teachers_from_14_in_file(link="https://new.guap.ru/i01/k14#tab_k14_2")
    find_id_teachers(link="https://guap.ru/rasp/")

if __name__=="__main__":
    main()