import requests
from bs4 import BeautifulSoup


def schedule_of_teachers(*, link: str, teacher: str)->dict:
    schedule_of_teacher = {}
    responce = requests.get(link).text
    soup = BeautifulSoup(responce, 'lxml')
    html_cod = str(soup.find(name='div', class_='result'))
    while '<h3>' in html_cod:
        index_h3=html_cod.find('<h3>')
        html_cod=html_cod[index_h3+4:]
        index_h3_next = html_cod.find('<h3>')
        index_day = html_cod.find('<')
        day_of_the_week=html_cod[:index_day]#Понедельник
        cod_of_day=html_cod[:index_h3_next]
        print(day_of_the_week)
        while '<h4>'in cod_of_day:
            index_h4 = cod_of_day.find('<h4>')
            cod_of_day = cod_of_day[index_h4 + 4:]
            index_h4_next = cod_of_day.find('<h4>')
            index_lesson = cod_of_day.find('<')
            num_of_lesson = cod_of_day[:index_lesson] #5 пара (16:40–18:10)
            cod_of_lesson=cod_of_day[:index_h4_next]
            up_or_down="верхняя и нижняя"
            if "title" in cod_of_lesson:
                index_up_or_down=cod_of_lesson.find('title')+7
                end_of_index_up_or_down=cod_of_lesson[index_up_or_down:].find('"')
                up_or_down=cod_of_lesson[index_up_or_down:index_up_or_down+end_of_index_up_or_down]#верхняя (нечетная)
                cod_of_lesson=cod_of_lesson[index_up_or_down+end_of_index_up_or_down:]

            index_type_of_lesson=cod_of_lesson.find('<b>')+3
            end_of_index_of_type=cod_of_lesson[index_type_of_lesson:].find('</b>')
            type_of_lesson=cod_of_lesson[index_type_of_lesson:index_type_of_lesson+end_of_index_of_type]#Л (или лр)

            cod_of_lesson=cod_of_lesson[index_type_of_lesson+end_of_index_of_type:]
            index_of_object=cod_of_lesson.find('–')
            end_of_index_of_object=cod_of_lesson.find('<em>')
            object=cod_of_lesson[index_of_object:end_of_index_of_object]#– Электроника

            cod_of_lesson=cod_of_lesson[end_of_index_of_object:]
            index_of_adress=cod_of_lesson.find('–')
            end_of_index_of_adress=cod_of_lesson.find('</em>')
            adress=cod_of_lesson[index_of_adress:end_of_index_of_adress]#– Гастелло 15, ауд. 31-02

            index_groups=cod_of_lesson.find('Группы:')+8
            cod_of_lesson=cod_of_lesson[index_groups:]
            soup = BeautifulSoup(cod_of_lesson, 'lxml')
            cod_of_groups=soup.find_all('a')
            groups=[]#['1241', '1242', '1243', '1245', '7241']
            for group in cod_of_groups:
                groups.append(group.text)
            schedule_of_teacher[teacher, day_of_the_week, num_of_lesson]=[up_or_down,type_of_lesson,object, adress,groups]

    return schedule_of_teacher
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
        link_with_id='https://guap.ru/rasp/?p='+str(teacher_id)
        #function

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
    #find_id_teachers(link="https://guap.ru/rasp/")
    shedule=schedule_of_teachers(link='https://guap.ru/rasp/?p=' + '675', teacher='Яблоков')
    print(shedule)
    #print(shedule)
    #675 - Яблоков
if __name__=="__main__":
    main()