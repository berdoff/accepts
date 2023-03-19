import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
import certifi
import datetime
from config import mongo,token_seraph
cluster=MongoClient(mongo,tlsCAFile=certifi.where())
db=cluster["UsersData"]
collection=db["logs"]
ONLINES=db["ONLINES"]
illegals=db["ILLEGALS"]
for i in illegals.find({"dostup":"1"}):
    illegals.update_one({"nick":i["nick"]},{"$set":{"otkazi":0}})
sess=requests.session()
xsrf=collection.find_one({"type":"token"})["session"]
print(xsrf)
sess.cookies.update({"laravel_session":xsrf,"XSRF-TOKEN":xsrf})
a=requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?&token={token_seraph}&server=21")
a=json.loads(a.text)["response"]
b = sess.get("https://arizonarp.logsparser.info/")
ONLINES.delete_many({})

def get_int_time(time):
    return int(int(time.split(":")[0]))*3600+int(time.split(":")[1])*60+int(time.split(":")[2])

def get_normal_time(time):
    hours=str(time//3600)
    if len(hours)<2:
        hours="0"+hours
    minutes=str(time%3600//60)
    if len(minutes)<2:
        minutes="0"+minutes
    seconds=str(time%60)
    if len(seconds)<2:
        seconds="0"+seconds
    return (hours+":"+minutes+":"+seconds)




def getonl(nick):

    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
    sess = requests.session()
    xsrf = collection.find_one({"type": "token"})["session"]
    sess.headers.update(header)
    sess.cookies.update({"laravel_session": xsrf, "XSRF-TOKEN": xsrf, "_token": "BQoKlviexTmz612jcCTHz5xzJn4d3KLyBXEYDa97"})
    a = sess.get("https://arizonarp.logsparser.info/")
    if "Queen-Creek" in a.text:
        date = datetime.datetime.now()+datetime.timedelta(days=1)
        year_today = date.year
        if len(str(date.month)) == 1:
            month_today = "0" + str(date.month)
        else:
            month_today = str(date.month)
        if len(str(date.day)) == 1:
            day_today = "0" + str(date.day)
        else:
            day_today = str(date.day)
        date = date - datetime.timedelta(days=15)
        year = str(date.year)
        if len(str(date.month)) == 1:
            month = "0" + str(date.month)
        else:
            month = str(date.month)
        if len(str(date.day)) == 1:
            day = "0" + str(date.day)
        else:
            day = str(date.day)
        logs=sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=login&type%5B%5D=disconnect&sort=desc&min_period={year}-{month}-{day}+00%3A00%3A00&max_period={year_today}-{month_today}-{day_today}+00%3A00%3A00&player={nick}&limit=1000")
        logs = BeautifulSoup(logs.text, "lxml")
        stroki = logs.find_all("tr")[1:]
        online={"online":{},"reports":{}}
        i=stroki[0]
        i = " ".join(i.text.split("I:")[0].strip().split())
        dday=i.split()[0]
        ctime=0
        gtime=0
        
        if "авторизовался" in i:
            date = datetime.datetime.now()-datetime.datetime.strptime(i.split()[0]+" "+i.split()[1], '%Y-%m-%d %H:%M:%S')
            date=datetime.datetime.strptime(str(date).split(".")[0], '%H:%M:%S')
            data=str(date.hour)+":"+str(date.minute)+":"+str(date.second)
            ctime+=get_int_time(data)
        for i in stroki:
            i = " ".join(i.text.split("I:")[0].strip().split())
            if "Есть" in i:
                if dday==i.split()[0]:
                    if get_int_time(i.split()[1])<get_int_time(i.split("сессии:")[1].split(",")[0]):
                        print(str(i.split()[1]),str(i.split("сессии:")[1].split(",")[0]))
                        ctime+=get_int_time(i.split()[1])
                        gtime=get_int_time(i.split("сессии:")[1].split(",")[0])-get_int_time(i.split()[1])
                    else:
                        gtime=0
                        ctime+=get_int_time(i.split("сессии:")[1].split(",")[0])
                else:
                    online["online"][dday]=get_normal_time(ctime)
                    ctime=0
                    ctime+=gtime
                    gtime=0
                    dday=i.split()[0]
                    if get_int_time(i.split()[1]) < get_int_time(i.split("сессии:")[1].split(",")[0]):
                        print(str(i.split()[1]), str(i.split("сессии:")[1].split(",")[0]))
                        ctime += get_int_time(i.split()[1])
                        gtime = get_int_time(i.split("сессии:")[1].split(",")[0]) - get_int_time(i.split()[1])
                    else:
                        gtime = 0
                        ctime += get_int_time(i.split("сессии:")[1].split(",")[0])
        
        k=1
        
        reports=0
        date = datetime.datetime.now()+datetime.timedelta(days=1)
        for i in range(15):
            date=date-datetime.timedelta(days=1)
            dd=""
            dd+=str(date.year)+"-"
            if len(str(date.month)) == 1:
                dd += "0" + str(date.month)+"-"
            else:
                dd += str(date.month)+"-"
            if len(str(date.day)) == 1:
                dd += "0" + str(date.day)
            else:
                dd += str(date.day)
            
            online["reports"][dd]=0
        logs=sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=report_answer&sort=desc&min_period={year}-{month}-{day}+00%3A00%3A00&max_period={year_today}-{month_today}-{day_today}+00%3A00%3A00&player={nick}&limit=1000&page={k}")
        logs = BeautifulSoup(logs.text, "lxml")
        logs=logs.find("table",class_="table table-hover")
        while "ответил на репорт" in logs.text:
            for i in online["reports"]:
                online["reports"][i]=online["reports"][i]+logs.text.count(i)
            print(k)        
            k+=1
            logs=sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=report_answer&sort=desc&min_period={year}-{month}-{day}+00%3A00%3A00&max_period={year_today}-{month_today}-{day_today}+00%3A00%3A00&player={nick}&limit=1000&page={k}")
            logs = BeautifulSoup(logs.text, "lxml")
            logs=logs.find("table",class_="table table-hover")
        online["reports"]["check"]="True"
        return online

    else:
        return {"status": "ne ok", "reason": "Логи не авторизованы"}
		
user = json.loads(requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?&token=berdoff21EbashitPchel&server=21").text)["response"]
for i in user:
    print(i["nick"])
    try:
        online=getonl(i["nick"])
        ONLINES.insert_one({"nick":i["nick"],"online":str(online),"server":"21"})
    except:
        ONLINES.insert_one({"nick":i["nick"],"online":"{'online': {}, 'reports': {'check': \"True\"}}","server":"21"})
	






