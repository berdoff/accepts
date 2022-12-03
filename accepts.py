import requests
from bs4 import BeautifulSoup
import json
from typing import Optional
import subprocess
import os
import vkbottle
from vkbottle import Keyboard, Callback, GroupTypes, GroupEventType,KeyboardButtonColor,ShowSnackbarEvent
from vkbottle.bot import Bot, Message
import imaplib
import time
from pymongo import MongoClient
import certifi
import datetime
import testip
from config import tok,token_seraph,mail,mail_pass,mongo,token_berdoff
import email
import asyncio


print(34)
cluster=MongoClient(mongo,tlsCAFile=certifi.where())
db=cluster["UsersData"]
collection=db["logs"]
xsrf=collection.find_one({"type":"token"})["session"]
ONLINES=db["ONLINES"]
forms=db["forms"]
collection=db["ILLEGALS"]
print(4)
archive=db["ILLEGALS_HISTORY"]
archive_gos=db["GOS_ARCHIVE_21"]
gos=db["GOS_21"]
sess=requests.session()

print(xsrf)
sess.cookies.update({"laravel_session":xsrf,"XSRF-TOKEN":xsrf})
servers={
    "1":"Phoenix",
    "2":"Tucson",
    "3":"Scottdale",
    "4":"Chandler",
    "5":"Brainburg",
    "6":"Saint-Rose",
    "7":"Mesa",
    "8":"Red-Rock",
    "9":"Yuma",
    "10":"Surprise",
    "11": "Prescott",
    "12": "Glendale",
    "13": "Kingman",
    "14": "Winslow",
    "15": "Payson",
    "16": "Gilbert",
    "17": "Show-Low",
    "18": "Casa-Grande",
    "19":"Page",
    "20":"Sun-City",
    "21":"Queen-Creek",
    "22":"Sedona",
    "23":"Holiday",
    "101":"Mobile 1",
    "102":"Mobile 2",
    "103":"Mobile 3",
    "201":"Vice-City 1"
}


def get_code(nick):
    time.sleep(10)
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(mail, mail_pass)
    mail.select("inbox")
    result, data = mail.search(None, "ALL")
    ids = data[0] # Получаем сроку номеров писем
    id_list = ids.split() # Разделяем ID писем
    take_code=False
    for i in range(1,20):
        latest_email_id = id_list[-i] # Берем последний ID
        result, data = mail.fetch(latest_email_id, "(RFC822)") # Получаем тело письма (RFC822) для данного ID
        raw_email = data[0][1] # Тело письма в необработанном виде
        # # включает в себя заголовки и альтернативные полезные нагрузки
        CODE=str(raw_email)
        if "cream.union-u.net" in str(raw_email) and "webmaster@union-u.net" in str(raw_email):
            CODE=CODE.split("Subject")[1].split("Delivered-To")[0].split("подтверждения администратора")[-1]
            CODE_TIME=str(raw_email).split("Received:")[1].split(";")[1].split(",")[1].split("(PST)")[0]
            CODE_TIME = "-".join(str(email.utils.parsedate_to_datetime(CODE_TIME)).split("-")[:-1])
            CODE_TIME=int(time.mktime(time.strptime(CODE_TIME,"%Y-%m-%d %H:%M:%S")))+39600
            if nick in CODE:
                CODE=CODE.split(f"{nick}:")[1].split("\\")[0].strip()
                current_time=int(str(time.time()).split(".")[0])
                code_old=str((current_time-CODE_TIME)//60)
                take_code=True
                return CODE+" "+code_old
    if not take_code:
        return("bad")

def chet_online(hours, minutes, seconds):
    minutes += seconds // 60
    seconds = seconds % 60
    hours += minutes // 60
    minutes = minutes % 60
    online = f'{hours}:{minutes}:{seconds}'
    return online

def get_online(nick, type, author_nick,server):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
    a = requests.get("http://berdoff.ru/getonline",data={"token": token_berdoff, "nick": nick,"server":server}).text
    user = json.loads(requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?nick={nick}&token={token_seraph}&server={server}",timeout=5).text)
    reps=False
    if len(user["response"]) != 0:
        reps=True
    online = json.loads(a)
    text_online = '⏳ ' + nick + ' ⏳' + '\n' + '\n'
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    monday_online = ''
    hours = 0
    minutes = 0
    seconds = 0
    all_reports=0
    for i in range(7):
        if i > 0:
            day = monday + datetime.timedelta(days=i)
        else:
            day = monday
        day_online="00:00:00"
        day_reps=0
        try:
            day_online = online["online"][f'{day}']
            if reps:
                try:
                    day_reps=online["reports"][f"{day}"]
                except:
                    day_reps=0
                all_reports+=int(day_reps)
                text_online += str(day) + ' ' + day_online + f' [R: {day_reps}]\n'
            else:
                text_online += str(day) + ' ' + day_online + '\n'
            

            day_hours = day_online.split(':')[0]
            day_minutes = day_online.split(':')[1]
            day_seconds = day_online.split(':')[2]
            hours += int(day_hours)
            minutes += int(day_minutes)
            seconds += int(day_seconds)

        except:
            if reps:
                text_online += str(day) + f' 00:00:00 [R: 0]\n'
            else:
                text_online += str(day) + ' ' + day_online + '\n'

    full_online = chet_online(hours, minutes, seconds)
    text_online += '\n' + 'Онлайн за последнюю неделю: ' + full_online
    if reps:
        text_online += '\n' + 'Репорта за последнюю неделю: ' + str(all_reports)
    return text_online

def norm_money(money):
    money=list(str(money))
    for i in range(len(money),0,-3):
        money.insert(i,".")
    money=money[:-1]
    return "".join(money)

def get_online_lw(nick, type, author_nick,server):
    reps=False
    
    if ONLINES.count_documents({"nick":nick})>0:
        a = ONLINES.find_one({"nick":nick})["online"]
        reps=True
    else:
        a = requests.get("http://berdoff.ru/getonline",data={"token": token_berdoff, "nick": nick,"server":server}).text
        user = json.loads(requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?nick={nick}&token={token_seraph}&server=21",timeout=5).text)
        if len(user["response"]) != 0:
            reps=True
            ONLINES.insert_one({"nick":nick,"online":str(a)})
    a=a.replace("\'","\"")
    online = json.loads(a)    
    #online = json.loads(a)
    text_online = '⏳ ' + nick + ' ⏳' + '\n' + '\n'
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())-datetime.timedelta(days=7)
    monday_online = ''
    hours = 0
    minutes = 0
    seconds = 0
    all_reports=0
    for i in range(7):
        if i > 0:
            day = monday + datetime.timedelta(days=i)
        else:
            day = monday
        day_online="00:00:00"
        day_reps=0
        try:
            day_online = online["online"][f'{day}']
            if reps:
                try:
                    day_reps=online["reports"][f"{day}"]
                except:
                    day_reps=0
                all_reports+=int(day_reps)
                text_online += str(day) + ' ' + day_online + f' [R: {day_reps}]\n'
            else:
                text_online += str(day) + ' ' + day_online + '\n'
            

            day_hours = day_online.split(':')[0]
            day_minutes = day_online.split(':')[1]
            day_seconds = day_online.split(':')[2]
            hours += int(day_hours)
            minutes += int(day_minutes)
            seconds += int(day_seconds)

        except:
            if reps:
                text_online += str(day) + f' 00:00:00 [R: 0]\n'
            else:
                text_online += str(day) + ' ' + day_online + '\n'

    full_online = chet_online(hours, minutes, seconds)
    text_online += '\n' + 'Онлайн за последнюю неделю: ' + full_online
    if reps:
        text_online += '\n' + 'Репорта за последнюю неделю: ' + str(all_reports)
    return text_online

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

bot = Bot(token=tok)





@bot.on.message(text="!ацепт")
async def accept(message: Message):
    global sess
    users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id

    nick = json.loads(requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?vk={id_authora}&token={token_seraph}&server=21",timeout=5).text)
    if len(nick["response"]) == 0:
        await message.answer(f"Вы не являетесь администратором")
    else:
        nick=nick["response"][0]["nick"]
        await message.answer(f"⌛ Идет загрузка информации для выдачи Аццепт-кода!")
        code=get_code(nick)
        if code!="bad":
            code_time = code.split()[1]
            code=code.split()[0]
            logs=sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=login&sort=desc&player={nick}&limit=1000")
            logs = BeautifulSoup(logs.text, "lxml")
            stroki = logs.find_all("tr")[1]
            data=stroki.text.split()[0]+" "+stroki.text.split()[1]
            reg_ip = stroki.find_all("span", class_="badge badge-primary")[0].text
            last_ip = stroki.find_all("span", class_="badge badge-secondary")[0].text
            l_joins=logs.text.count(last_ip.split(".")[0]+"."+last_ip.split(".")[1])
            distance = testip.get_distance_between_ip(reg_ip, last_ip)
            last_info = testip.get_info_by_ip(last_ip)
            last_city = last_info["city"]
            last_region = last_info["region"]
            last_org = " ".join(last_info["org"].split()[:7])
            reg_info = testip.get_info_by_ip(reg_ip)
            reg_city = reg_info["city"]
            reg_region = reg_info["region"]
            reg_org = " ".join(reg_info["org"].split()[:7])
            client_type=stroki.text.split("клиента:")[1].split("I")[0]
            ans_msg=f"""@id{id_authora}({nick}) запрашивает Accept!

❌ [Местоположение] ❌

♻ REG-IP: [{reg_ip}] - [{reg_city} / {reg_region}]
♻ REG-PROVIDER: [{reg_org}]
♻ LAST-IP: [{last_ip}] - [{last_city} / {last_region}]
♻ LAST-PROVIDER: [{last_org}]
♻ Входов с LAST-IP: {l_joins}

❌ Расстояние от R-IP до L-IP {distance} Км.

❌ Тип клиента: {client_type}

"""
            KEYBOARD = (
                Keyboard(inline=True)
                    .add(Callback("Выдать", payload={"cmd": "accept","nick":nick,"vk":id_authora,"code":code,"time":code_time}), color=KeyboardButtonColor.POSITIVE)
                    .add(Callback("Отказать", payload={"cmd": "ne accept","nick":nick,"vk":id_authora}), color=KeyboardButtonColor.NEGATIVE)
                    .get_json()
            )

            await message.answer(f" @id{id_authora}({nick})\n\nОжидайте выдачи Аццепт-кода!\nПосле перезахода КОД становится недействительным!")
            await bot.api.messages.send(chat_id=3,message=ans_msg,keyboard=KEYBOARD,random_id=0)
        else:
            await message.answer(f"""Новый accept-code не найден!

1) Напишите в игре /qaccadmin
2) Выберите ник "Rafael_Camilleri"
3) Через 15 секунд повторите попытку !ацепт""")

@bot.on.message(text="/id_be")
async def hi_handler(message: Message):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.reply_message.from_id
    await message.answer(f"{message.chat_id}")

@bot.on.message(text=["/lhistory <data_start> <data_end>","/lhistory"])
async def lhistory(message: Message,data_start: Optional[str] = None,data_end: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=str(message.reply_message.from_id)
    if str(message.chat_id)=="3":
        if data_start!=None and data_end!=None:
            await message.answer("⚙ Загрузка информации о поставленных/снятых лидерах ⚙")
            data_start = datetime.datetime.strptime(data_start, '%d.%m.%Y')
            data_start = str(data_start.day) + '.' + str(data_start.month) + '.' + str(data_start.year)
            data_end = datetime.datetime.strptime(data_end, '%d.%m.%Y')
            data_end = str(data_end.day) + '.' + str(data_end.month) + '.' + str(data_end.year)
            leaders_add=[]
            leaders_del=[]
            while data_start!=data_end:
                leaders_add.append(collection.find({"add_data":str(data_start),"dostup":"1"}))
                leaders_add.append(gos.find({"add_data": str(data_start),"dostup":"1"}))
                leaders_add.append(archive_gos.find({"add_data": str(data_start), "dostup": "1"}))
                leaders_add.append(archive.find({"add_data": str(data_start), "dostup": "1"}))
                for i in archive.find():
                    if data_start in i["snyatie"]:
                        leaders_del.append(i)
                for i in archive_gos.find():
                    if data_start in i["snyatie"]:
                        leaders_del.append(i)
                data_start=datetime.datetime.strptime(data_start, '%d.%m.%Y')
                data_start=(data_start+datetime.timedelta(days=1))
                data_start=str(data_start.day)+'.'+str(data_start.month)+'.'+str(data_start.year)
            spisok=""

            for i1 in leaders_add:
                for i in i1:
                    try:
                        spisok+=i["add_data"]+" поставлен "+i["role"]+" "+i["frac"]+" "+i["nick"]+" "+i["type_add"]+"\n"
                    except:
                        spisok+=i["add_data"]+" поставлен "+i["rank"]+" "+i["frac"]+" "+i["nick"]+" "+i["type_add"]+"\n"
            spisok+="------------------------------------------------------------------------\n"

            for i in leaders_del:
                try:
                    spisok+=i["snyatie"].split()[0]+" снят "+i["role"]+" "+i["frac"]+" "+i["nick"]+" Причина: "+" ".join(i["snyatie"].split()[1:])+"\n"
                except:
                    spisok+=i["snyatie"].split()[-1]+" снят "+i["rank"]+" "+i["frac"]+" "+i["nick"]+" Причина: "+" ".join(i["snyatie"].split()[:-1])+"\n"
            await message.answer(spisok)
        else:
            await message.answer("❗Используйте /lhistory [дата начала] [дата конца(не включительно)]")


@bot.on.message(text=["/logs <nick> <server>","/logs","/logs <nick>"])
async def log(message: Message,nick: Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if (server!=None and str(message.chat_id)=="3") or (server!=None and str(id_authora)=="178391887"):
        pass
    else:
        server="21"   

    if str(message.chat_id)=="5" or str(message.chat_id)=="8" or str(message.chat_id)=="3" or str(id_authora)=="178391887":
        if nick!=None:
            await message.answer("Началась загрузка, примерное время загрузки 30 секунд")
            a = requests.get("http://berdoff.ru/loadlogsdawdawdwadwadwadwadwa2121",data={"token": token_berdoff, "nick": nick,"server":server}).text
            await message.answer(f"Загружен лог на 7 дней\nhttp://berdoff.ru/getlogs?token={a}")
        else:
            await message.answer("Используйте /logs [id/nick]")


@bot.on.message(text=["/game <fforms>"])
async def game_forms(message: Message,fforms: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if str(message.chat_id)=="3":
        if forms.count_documents({"user":id_authora})!=0:
            if forms.find_one({"user":id_authora})["dostup"]=="1":
                forms_bd=db["forms"]
                a=message.text.replace("/game","").strip()
                a=a.split("\n")
                nicks=[]
                if len(a)>10:
                    await message.answer("Не больше 10 форм!")
                else:
                    for i in a:
                        forms_bd.insert_one({"forma":i,"author":id_authora,"status":0})
                    await message.answer("Следующие формы записаны: \n\n"+"\n".join(a)+"\n\nОжидайте информации по ним через минуту.")
                    await asyncio.sleep(60)
                    date=datetime.datetime.now()
                    date=date-datetime.timedelta(minutes=1)
                    year=date.year
                    if len(str(date.month))==1:
                        month="0"+str(date.month)
                    else:
                        month=str(date.month)
                    if len(str(date.day))==1:
                        day="0"+str(date.day)
                    else:
                        day=str(date.day)
                    if len(str(date.hour))==1:
                        hour="0"+str(date.hour)
                    else:
                        hour=str(date.hour)
                    if len(str(date.minute))==1:
                        minute="0"+str(date.minute)
                    else:
                        minute=str(date.minute)
                    logs=sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=rmute&type%5B%5D=unrmute&type%5B%5D=agl&type%5B%5D=givedonate&type%5B%5D=ao_chat&type%5B%5D=ban&type%5B%5D=jail&type%5B%5D=mute&type%5B%5D=warn&type%5B%5D=banip&type%5B%5D=unban&type%5B%5D=unjail&type%5B%5D=unmute&type%5B%5D=unwarn&type%5B%5D=unbanip&type%5B%5D=unwarn_talon&type%5B%5D=inventory_admin&sort=desc&min_period={year}-{month}-{day}+{hour}%3A{minute}%3A00&player=QueenBot")
                    logs=BeautifulSoup(logs.text,"lxml")
                    stroki=logs.find_all("tr")[1:]
                    forms_plus=[]
                    if len(stroki)!=0:
                        for i in stroki:
                            forms_plus.append(" ".join(i.text.split("I:")[0].strip().split()))
                    await message.answer("Выданные в игре формы:\n\n"+"\n".join(forms_plus))
            else:
                await message.answer("Access denied")
        else:
            await message.answer("Access denied")

@bot.on.message(text=["/onlines <lvl>"])
async def online(message: Message, lvl: Optional[str] = None):
    if message.chat_id==5:
        on_ans=""
        lvl=lvl.strip()
        if lvl=="1-2":
            on_ans="""📝Statistic of admistrators 1-2-х LVL for last week\n\n"""
        elif lvl=="3-4":
            on_ans="""📝Statistic of admistrators 3-4-х LVL for last week\n\n"""
        else:
            await message.answer("❌ Ошибка определения лвлов [1-2/3-4]")
        if "Statistic of admistrators" in on_ans:
            await message.answer("✅ Waiting")
            adms=[]
            a=requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?&token={token_seraph}&server=21",timeout=5)
            a=json.loads(a.text)["response"]
            for i in a:
                if int(i["lvl"])<=int(lvl.split("-")[1]) and int(i["lvl"])>=int(lvl.split("-")[0]):
                    onl=get_online_lw(i["nick"], 1, i["nick"],"21")
                    online=onl.split("Онлайн за последнюю неделю: ")[1].split("\n")[0]
                    onl_int=3600*int(online.split(":")[0])+60*int(online.split(":")[1])+int(online.split(":")[2])
                    reps=int(onl.split("Репорта за последнюю неделю: ")[1])
                    if (int(online.split(":")[0])>=22) and (lvl=="1-2" or i["lvl"]=="3") or (int(online.split(":")[0])>=19 and i["lvl"]=="4"):
                        ch_onl="✅"
                    elif (int(online.split(":")[0])>=15 and int(online.split(":")[0])<22 and (lvl=="1-2" or i["lvl"]=="3")) or (int(online.split(":")[0])>=14 and int(online.split(":")[0])<19 and i["lvl"]=="4"):
                        ch_onl="⚠"
                    else:
                        ch_onl="⛔"
                    if (int(reps)>=1500 and lvl=="1-2") or (int(reps)>=700 and i["lvl"]=="3") or (int(reps)>=600 and i["lvl"]=="4"):
                        ch_reps="✅"
                    elif (int(reps)>=1000 and int(reps)<1500 and lvl=="1-2") or (int(reps)>=500 and int(reps)<700 and i["lvl"]=="3") or (int(reps)>=400 and int(reps)<600 and i["lvl"]=="4"):
                        ch_reps="⚠"
                    else:
                        ch_reps="⛔"
                    adms.append({"nick":i["nick"],"online":online,"reports":reps,"onl_int":onl_int,"ch_reps":ch_reps,"ch_onl":ch_onl,"lvl":i["lvl"]})
                    time.sleep(2)
            #await message.answer(str(adms))
            k=1
            for i in sorted(adms,key=lambda k:(k["onl_int"],k["reports"]),reverse=True):
                on_ans+=f"[{k}]"+" "+i["nick"]+" ["+i["lvl"]+"] Play: "+i["online"]+" "+i["ch_onl"]+" Reps: "+str(i["reports"])+" "+i["ch_reps"]+"\n"
                k+=1
            await message.answer(on_ans)
                        


                




    


@bot.on.message(text=["/myonl","/myonline"])
async def myonline(message: Message):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id
    nick = json.loads(requests.get(
        f"https://seraphtech.site/api/v2/forum.getAdmins?vk={id_authora}&token={token_seraph}&server=21",timeout=5).text)
    if len(nick["response"]) == 0:
        await message.answer(f"❌  Вы не являетесь администратором")
    else:
        nick = nick["response"][0]["nick"]
        await message.answer(f"⚙ {nick} началась загрузка онлайна")
        online = get_online(nick, 1, nick,"21")
        await message.answer(online)


@bot.on.message(text=["/online <nick>","/onl <nick>","/onl","/online"])
async def online(message: Message, nick:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.from_id
    if len(message.text.split())<4 and len(message.text.split())>1:
        try:
            server=message.text.split()[2].strip()
        except:
            server="21"
        if server in servers:
            await message.answer(f"⚙ {nick} началась загрузка онлайна "+servers[server])
            online = get_online(nick, 1, nick,server)
            await message.answer(online)
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("/onl [nick] [server(не обязательно)]")

@bot.on.message(text=["/lw_online <nick>","/lw_onl <nick>","/lw_onl","/lw_online"])
async def lww_online(message: Message, nick: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.from_id
    if len(message.text.split())<4 and len(message.text.split())>1:
        try:
            server=message.text.split()[2].strip()
        except:
            server="21"
        nick=message.text.split()[1]
        if server in servers:
            await message.answer(f"⚙ {nick} началась загрузка онлайна "+servers[server])
            online = get_online_lw(nick, 1, nick,server)
            await message.answer(online)
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("/lw_onl [nick] [server(не обязательно)]")


@bot.on.message(text=["/info <nick>","/info"])
async def info(message: Message, nick: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id
    if forms.find_one({"user":str(id_authora)})["dostup"]=="1":
        if len(message.text.split())<4 and len(message.text.split())>1:
            try:
                server=message.text.split()[2].strip()
            except:
                server="21"
            nick=message.text.split()[1].strip()
            a="Сервер"
            if "Сервер" in a:
                logs=sess.get(f"https://arizonarp.logsparser.info/?server_number={server}&type%5B%5D=login&sort=desc&player={nick}")
                logs=BeautifulSoup(logs.text,"lxml")
                stroka=logs.find_all("tr")[1]
                reg_ip = stroka.find_all("span", class_="badge badge-primary")[0].text
                last_ip = stroka.find_all("span", class_="badge badge-secondary")[0].text
                last_info = testip.get_info_by_ip(last_ip)
                last_city = last_info["city"]
                last_region = last_info["region"]
                reg_info = testip.get_info_by_ip(reg_ip)
                reg_city = reg_info["city"]
                reg_region = reg_info["region"]
                nick=stroka.text.split()[3]
                last_auth=stroka.text.split()[0]+" "+stroka.text.split()[1]
                id_acc=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[0].find("code").text
                await message.answer(f"Загрузка {nick}[{id_acc}] Server: {server}")
                logs=sess.get(f"https://arizonarp.logsparser.info/?server_number={server}&type%5B%5D=login&type%5B%5D=disconnect&sort=desc&player={id_acc}")
                logs=BeautifulSoup(logs.text,"lxml")
                stroka=logs.find_all("tr")[1:]
                if "авторизовался" in stroka[0].text:
                    status="В игре✅"
                else:
                    status="Не в сети⛔"
                for i in stroka:
                    if "авторизация: Есть" in i.text or "авторизовался" in i.text:
                        stroka=i
                        break
                nick=stroka.text.split()[3]
                vc_money=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[1].find("code").text
                lich1_money=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[2].find("code").text
                lich2_money=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[3].find("code").text
                lich3_money=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[4].find("code").text
                deposit=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[5].find("code").text
                if lich1_money=="4,294,967,295":
                    lich1_money="0"
                if lich2_money=="4,294,967,295":
                    lich2_money="0"
                if lich3_money=="4,294,967,295":
                    lich3_money="0"
                money_nal=stroka.find_all("code")[1].text
                money_bank=stroka.find_all("code")[2].text
                donate=stroka.find_all("code")[3].text
                money_all=norm_money(int(money_nal.replace(",",""))+int(money_bank.replace(",",""))+int(deposit.replace(",",""))+int(lich1_money.replace(",",""))+int(lich2_money.replace(",",""))+int(lich3_money.replace(",","")))
                lvl_adm=stroka.find_all("div",class_="app__hidden")[0].find_all("li")[6].find("code").text
                if lvl_adm!="0":
                    lvl_adm="Уровень адм: "+lvl_adm+"\n"
                else:
                    lvl_adm=""

                try:
                    ban=sess.get(f"https://arizonarp.logsparser.info/?server_number={server}&type%5B%5D=ban&type%5B%5D=unban&sort=desc&player={nick}")
                    logs=BeautifulSoup(ban.text,"lxml")
                    stroki=logs.find_all("tr")[1]
                    if "забанил" in stroki.text:
                        if stroki.text.split()[6]==nick:
                            day=int(stroki.text.split()[8])
                            last_ban=datetime.datetime.strptime(stroki.text.split()[0]+" "+stroki.text.split()[1], '%Y-%m-%d %H:%M:%S')
                            last_ban=int(str(time.mktime(last_ban.timetuple())).split(".")[0])
                            now_time=int(str(time.time()).split(".")[0])+10800
                            if (now_time-int(last_ban))<(day*86400):
                                bban=" ".join(stroki.text.split("I:")[0].strip().split())
                                prichina=bban.split("причина: ")[1]
                                ban_do=str(datetime.datetime.utcfromtimestamp(int(last_ban)+(day*86400)).strftime('%Y-%m-%d %H:%M:%S'))
                                bban=f"\n⛔Забанен за {prichina}⛔\nЗабанил: "+bban.split()[3]+"\nДата блокировки: "+stroki.text.split()[0]+" "+stroki.text.split()[1]+f"\nБан до {ban_do}"
                            else:
                                bban="✅ Аккаунт не заблокирован"
                        else:
                            bban="✅ Аккаунт не заблокирован"
                    else:
                        bban="✅ Аккаунт не заблокирован"
                except:
                    bban="✅ Аккаунт не заблокирован"

                vk=""
                email=""
                register=""
                
                try:
                    logs=sess.get(f"https://arizonarp.logsparser.info/?server_number={server}&type%5B%5D=mail&type%5B%5D=register&type%5B%5D=vk_attach&type%5B%5D=vk_detach&sort=desc&player={id_acc}")
                    logs=BeautifulSoup(logs.text,"lxml")
                    stroki=logs.find_all("tr")[1:]
                    vk="\n"
                    email="\n"
                    for i in stroki:
                        a=" ".join(i.text.split("I:")[0].strip().split())
                        change_ip = i.find_all("span", class_="badge badge-secondary")[0].text
                        if "почту" in a:
                            first_pochta=cfDecodeEmail(i.find_all(href="/cdn-cgi/l/email-protection")[0]["data-cfemail"])
                            second_pochta=cfDecodeEmail(i.find_all(href="/cdn-cgi/l/email-protection")[1]["data-cfemail"])
                            #a=a.replace("[email protected]",cfDecodeEmail(i.find(href="/cdn-cgi/l/email-protection")["data-cfemail"]))
                            #a=a[:16] + " "+a.split("почту")[1].split("на")[0] + " -> " + a.split("на")[1]
                            a=a[:16]+" "+first_pochta+" -> "+second_pochta
                            email+=a+f"\nL-IP: {change_ip}\n"
                        elif "ВКонтакте" in a:
                            a=a[:16]+" "+a.split()[4]+" "+a.split("ВКонтакте")[1]
                            vk+=a+f"\nL-IP: {change_ip}\n"
                        elif "зарегистрировался на" in a:
                            register=a.split()[0]+" "+a.split()[1]
                    if len(vk)<5:
                        vk="[Изменений в логах не обнаружено]"
                    if len(email)<5:
                        email="[Изменений в логах не обнаружено]"
                    if len(register)<4:
                        register="[Дата регистрации не найдена]"
                except:
                    vk="[Изменений в логах не обнаружено]"
                    email="[Изменений в логах не обнаружено]"

                await message.answer(f"Ник: {nick}[{id_acc}] Server: [{server}]\n{lvl_adm}Статус: {status}\nAz-Coin: {donate}\nНа руках: {money_nal}$\nБанк: {money_bank}$\nДепозит: {deposit}$\nVC: {vc_money}$\nЛичный счет №1: {lich1_money}$\nЛичный счет №2: {lich2_money}$\nЛичный счет №3: {lich3_money}$\nВсего денег: {money_all}$\nИзменения по почте:\n {email}\nИзменения по вк:\n {vk}\nПоследний вход: {last_auth}\nРегистрация: {register}\nR-IP: {reg_ip} [{reg_city},{reg_region}]\nL-IP: {last_ip} [{last_city},{last_region}]\n{bban}")
        else:
            await message.answer("/info [nick] [server(по умолчанию 21)]")      
            
    else:
        await message.answer("Access denied")

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def handle_message_event(event: GroupTypes.MessageEvent):
    # event_data parameter accepts three object types
    # "show_snackbar" type
    if event.object.payload["cmd"]=="accept":
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=ShowSnackbarEvent(text="☑ Ацепт код отправлен").json(),
            payload=event.object.payload
        )
        if event.object.user_id==event.object.payload["vk"]:
            await bot.api.messages.send(chat_id=3, message=f'@id{event.object.user_id}(❌) Нельзя выдать ацепт самому себе!', random_id=0)
        else:
            await bot.api.messages.send(chat_id=3, message=f'@id{event.object.user_id}(☑) Ацепт код отправлен  @id'+str(event.object.payload["vk"])+"("+event.object.payload["nick"]+")", random_id=0)
            await bot.api.messages.send(chat_id=2, message="@id"+str(event.object.payload["vk"])+"("+event.object.payload["nick"]+") "+" Ваш код: "+event.object.payload["code"]+"  | Коду: "+str(event.object.payload["time"])+"  минут",random_id=0)

    elif event.object.payload["cmd"]=="ne accept":
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=ShowSnackbarEvent(text="‼ Ацепт код отказан ‼").json(),
        )
        await bot.api.messages.send(chat_id=2, message="@id"+str(event.object.payload["vk"])+"("+event.object.payload["nick"]+") "+" в выдаче кода отказано!",random_id=0)
        await bot.api.messages.send(chat_id=3,message='‼ Ацепт код отказан ‼\n✅ Сообщение об отказе ' + f'@id{event.object.user_id}(отправлено)',random_id=0)


bot.run_forever()
    






