import requests
from bs4 import BeautifulSoup
import json
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
        while '<h4>'in cod_of_day:
            index_h4 = cod_of_day.find('<h4>')
            cod_of_day = cod_of_day[index_h4 + 4:]
            index_h4_next = cod_of_day.find('<h4>')
            index_lesson = cod_of_day.find('<')
            num_of_lesson = cod_of_day[:index_lesson] #5 пара (16:40–18:10)
            cod_of_lesson=cod_of_day[:index_h4_next]
            up_or_down=None
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
            if 'Группы' in cod_of_lesson:
                index_groups=cod_of_lesson.find('Группы:')+8
            else:
                index_groups = cod_of_lesson.find('Группа:') + 8
            cod_of_lesson=cod_of_lesson[index_groups:]
            if 'b' not in cod_of_lesson:
                soup = BeautifulSoup(cod_of_lesson, 'lxml')
                cod_of_groups=soup.find_all('a')
                groups=[]#['1241', '1242', '1243', '1245', '7241']
            else:
                index_of_next=cod_of_lesson.find('b')
                soup = BeautifulSoup(cod_of_lesson[:index_of_next-1], 'lxml')
                cod_of_groups = soup.find_all('a')
                groups = []  # ['1241', '1242', '1243', '1245', '7241']
            for group in cod_of_groups:
                groups.append(group.text)
            if (up_or_down):
                schedule_of_teacher[str(day_of_the_week+' '+num_of_lesson+' '+up_or_down)] = [type_of_lesson, object, adress, groups]
            else:
                schedule_of_teacher[str(day_of_the_week+ ' '+num_of_lesson+' '+'нижняя (четная)')] = [type_of_lesson, object, adress, groups]
                schedule_of_teacher[str(day_of_the_week+' '+num_of_lesson+' '+'верхняя (нечетная)')] = [type_of_lesson, object, adress, groups]
            if '<div' in cod_of_lesson:
                index_of_next=cod_of_lesson.find('<div')
                index_next_lesson = cod_of_day.find('<h4>')
                cod_of_day = '<h4>' + num_of_lesson + '</h4>' + cod_of_lesson[index_of_next:] + cod_of_day[
                                                                                                index_next_lesson:]

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
                teachers_id_from_14.append((teachers_id,teachers_fio))

    schedule={}
    for teacher_id, teachers_fio in teachers_id_from_14:
        link_with_id='https://guap.ru/rasp/?p='+str(teacher_id)
        schedule_of_teach = schedule_of_teachers(link=link_with_id, teacher=teachers_fio)
        schedule[teachers_fio] = schedule_of_teach
    with open("shcedule.json", 'w', encoding='utf-8') as file:
        file.write(json.dumps(schedule, indent=4, ensure_ascii=False))
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

def schedule_of_audience():
    responce = requests.get('https://guap.ru/rasp/').text
    soup = BeautifulSoup(responce, 'lxml')
    soup=soup.find(attrs={'name':'ctl00$cphMain$ctl08'})
    soup=(soup.find_all('option')[1:])
    audiences=[]
    for audit in soup:
        id_audit=(str(audit).split('"')[1])
        num_audit=audit.text
        audiences.append((id_audit,num_audit))
    id_korpuses= [(1, 'Б. Морская 67'),(3, "Гастелло 15"),(4, "Московский 149в"),(5, "Ленсовета 14")]
    full_schedule={}
    for i, korpus in id_korpuses:
        schedule_of_korpus={}
        for id_audit, num_audit in (audiences):
            schedule_of_audit={}
            responce = requests.get('https://guap.ru/rasp/?b='+str(i)+'&r='+str(id_audit)).text
            soup = BeautifulSoup(responce, 'lxml')
            html_cod=str(soup)
            if '<h4>' not in html_cod:
                continue

            while '<h3>' in html_cod:
                index_h3 = html_cod.find('<h3>')
                html_cod = html_cod[index_h3 + 4:]

                index_h3_next = html_cod.find('<h3>')
                index_day = html_cod.find('<')
                day_of_the_week = html_cod[:index_day]  # Понедельник
                cod_of_day = html_cod[:index_h3_next]
                while '<h4>' in cod_of_day:
                    index_h4 = cod_of_day.find('<h4>')
                    cod_of_day = cod_of_day[index_h4 + 4:]
                    index_h4_next = cod_of_day.find('<h4>')
                    index_lesson = cod_of_day.find('<')
                    num_of_lesson = cod_of_day[:index_lesson]  # 5 пара (16:40–18:10)
                    cod_of_lesson = cod_of_day[:index_h4_next]
                    up_or_down = None
                    if "title" in cod_of_lesson:
                        index_up_or_down = cod_of_lesson.find('title') + 7
                        end_of_index_up_or_down = cod_of_lesson[index_up_or_down:].find('"')
                        up_or_down = cod_of_lesson[
                                     index_up_or_down:index_up_or_down + end_of_index_up_or_down]  # верхняя (нечетная)
                        cod_of_lesson = cod_of_lesson[index_up_or_down + end_of_index_up_or_down:]
                    index_type_of_lesson = cod_of_lesson.find('<b>') + 3
                    end_of_index_of_type = cod_of_lesson[index_type_of_lesson:].find('</b>')
                    type_of_lesson = cod_of_lesson[
                                     index_type_of_lesson:index_type_of_lesson + end_of_index_of_type]  # Л (или лр)

                    cod_of_lesson = cod_of_lesson[index_type_of_lesson + end_of_index_of_type:]
                    index_of_object = cod_of_lesson.find('–')
                    end_of_index_of_object = cod_of_lesson.find('<em>')
                    object = cod_of_lesson[index_of_object:end_of_index_of_object]  # – Электроника

                    if 'Преподаватель' in cod_of_lesson:
                        index_of_prep = cod_of_lesson.find('Преподаватель')
                        cod_of_lesson = cod_of_lesson[index_of_prep:]
                        index_of_prep = cod_of_lesson.find('>')
                        end_of_index_of_prep = cod_of_lesson.find('</a>')
                        prep = cod_of_lesson[index_of_prep+1:end_of_index_of_prep]  # Бибарсов М.Р. - доцент, канд. техн. наук, доцент
                    else:
                        index_of_prep = cod_of_lesson.find('Преподаватели')
                        cod_of_lesson = cod_of_lesson[index_of_prep:]
                        index_of_prep = cod_of_lesson.find('<')
                        end_of_index_of_prep = cod_of_lesson.find('</span>')
                        preps = cod_of_lesson[
                        index_of_prep:end_of_index_of_prep]  # Бибарсов М.Р. - доцент, канд. техн. наук, доцент
                        soup = BeautifulSoup(preps, 'lxml')
                        preps=soup.find_all('a')
                        prep=''
                        for j in range(len(preps)-1):
                            prep+=preps[j].text+'; '
                        try:
                            prep+=preps[-1].text
                        except IndexError:
                            prep=''
                    if 'Группы' in cod_of_lesson:
                        index_groups = cod_of_lesson.find('Группы:') + 8
                    else:
                        index_groups = cod_of_lesson.find('Группа:') + 8
                    cod_of_lesson = cod_of_lesson[index_groups:]
                    if 'b' not in cod_of_lesson:
                        soup = BeautifulSoup(cod_of_lesson, 'lxml')
                        cod_of_groups = soup.find_all('a')
                        groups = []  # ['1241', '1242', '1243', '1245', '7241']
                    else:
                        index_of_next = cod_of_lesson.find('b')
                        soup = BeautifulSoup(cod_of_lesson[:index_of_next - 1], 'lxml')
                        cod_of_groups = soup.find_all('a')
                        groups = []  # ['1241', '1242', '1243', '1245', '7241']
                    for group in cod_of_groups:
                        groups.append(group.text)
                    if (up_or_down):
                        schedule_of_audit[str(day_of_the_week + ' ' + num_of_lesson + ' ' + up_or_down)] = [
                            type_of_lesson, object, prep, groups]
                    else:
                        schedule_of_audit[str(day_of_the_week + ' ' + num_of_lesson + ' ' + 'нижняя (четная)')] = [
                            type_of_lesson, object, prep, groups]
                        schedule_of_audit[str(day_of_the_week + ' ' + num_of_lesson + ' ' + 'верхняя (нечетная)')] = [
                            type_of_lesson, object, prep, groups]
                    if '<div' in cod_of_lesson:
                        index_of_next = cod_of_lesson.find('<div')
                        index_next_lesson=cod_of_day.find('<h4>')
                        cod_of_day = '<h4>'+ num_of_lesson + '</h4>' + cod_of_lesson[index_of_next:]+cod_of_day[index_next_lesson:]
            schedule_of_korpus[num_audit]=schedule_of_audit

        full_schedule[korpus]=schedule_of_korpus
    with open("shcedule_of_audiences.json", 'w', encoding='utf-8') as file:
        file.write(json.dumps(full_schedule, indent=4, ensure_ascii=False))

def main():
    write_teachers_from_14_in_file(link="https://new.guap.ru/i01/k14#tab_k14_2")
    find_id_teachers(link="https://guap.ru/rasp/")
    schedule_of_audience()

if __name__=="__main__":
    main()