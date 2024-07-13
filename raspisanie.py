from json import *
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
    """rasp=open("shcedule.txt").readlines()
    begin=0
    while rasp[begin]!=teacher:
        begin+=1
    end=begin+1
    while end<len(rasp) and rasp[end]!="" and rasp[end]!="\n":
        end+=1
    return rasp[begin+1: end]
    """
