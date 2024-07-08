def get_name(message):
    teachers=open("teachers_from_14.txt").readlines()
    for teacher in teachers:
        if message.lower() in teacher.lower():
            return teacher
    return ""
def get_rasp(teacher):
    rasp=open("shcedule.txt").readlines()
    begin=0
    while rasp[begin]!=teacher:
        begin+=1
    end=begin+1
    while end<len(rasp) and rasp[end]!="" and rasp[end]!="\n":
        end+=1
    return rasp[begin+1: end]