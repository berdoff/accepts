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
import aiohttp



cluster=MongoClient(mongo,tlsCAFile=certifi.where())
db=cluster["UsersData"]
collection=db["logs"]
xsrf=collection.find_one({"type":"token"})["session"].replace("\'","\"")
sess=requests.session()
sess.cookies.update(json.loads(xsrf))
ONLINES=db["ONLINES"]
loggs=db["logs"]
forms=db["forms"]
collection=db["ILLEGALS"]
archive=db["ILLEGALS_HISTORY"]
archive_gos=db["GOS_ARCHIVE_21"]
gos=db["GOS_21"]

slets_bd=db["SLET_LOGS_21"]
header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}

private_fracs={
    "18":"La Cosa Nostra",
    "101":"Tierra Robada Bikers",
    "25":"Night Wolfs",
    "26":"Радиоцентр СФ",
    "24":"Радиоцентр ЛВ",
    "8":"Больница СФ",
    "201":"Больница Джефферсон",
    "28":"Страховая компания"
}

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

def get_id_by_tag(msg):
    return str(msg).split("id")[1].split("|")[0]

def get_code(nick):
    time.sleep(10)
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login("hrhhhdki@gmail.com", "gqpizosplmcnftst")
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

async def get_online(nick, type, author_nick,server):
    async with aiohttp.ClientSession() as sess:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
        a = await sess.get("https://berdoff.ru/getonline",data={"token": token_berdoff, "nick": nick,"server":server})
        a= await a.text()
        if ONLINES.count_documents({"nick":nick,"server":server})==0:
            ONLINES.insert_one({"nick":nick,"online":str(a),"server":server})
        online = json.loads(a)
        reps=bool(online["reports"]["check"])
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


async def get_online_month(nick, type, author_nick,server):
    async with aiohttp.ClientSession() as sess:
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
        a = await sess.get("https://berdoff.ru/getmonline",data={"token": token_berdoff, "nick": nick,"server":server})
        a= await a.text()
        if ONLINES.count_documents({"nick":nick,"server":server})==0:
            ONLINES.insert_one({"nick":nick,"online":str(a),"server":server})
        online = json.loads(a)
        reps=bool(online["reports"]["check"])
        text_online = '⏳ ' + nick + ' ⏳' + '\n' + '\n'
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=31)
        monday_online = ''
        hours = 0
        minutes = 0
        seconds = 0
        all_reports=0
        for i in range(31):
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
        text_online += '\n' + 'Онлайн за месяц: ' + full_online
        if reps:
            text_online += '\n' + 'Репорта за месяц: ' + str(all_reports)
        return text_online


async def get_reports_month(server,days):
    async with aiohttp.ClientSession() as sess:
        
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
        a = await sess.get("https://berdoff.ru/api/mreports",data={"token": token_berdoff, "server":server,"days":days},timeout=6000)
        a= await a.text()
        online = json.loads(a)
        
        text_reports = '⏳ ' + servers[server] + ' ⏳' + '\n' + '\n'
        date = datetime.datetime.now()-datetime.timedelta(days=int(days))
        for i in range(int(days)):
            
            date=date+datetime.timedelta(days=1)
            year = str(date.year)
            if len(str(date.month)) == 1:
                month = "0" + str(date.month)
            else:
                month = str(date.month)
            if len(str(date.day)) == 1:
                day = "0" + str(date.day)
            else:
                day = str(date.day)
            day_reps=0
            
            try:
                day_reps=online["reports"][f"{year}-{month}-{day}"]
            except:
                pass
            text_reports+=f"{year}-{month}-{day}"+f": {day_reps}\n"
        
    
        return text_reports

def norm_money(money):
    money=list(str(money))
    for i in range(len(money),0,-3):
        money.insert(i,".")
    money=money[:-1]
    return "".join(money)

async def get_online_lw(nick, type, author_nick,server):
    if ONLINES.count_documents({"nick":nick,"server":server})!=0 and not "Логи не авторизованы" in str(ONLINES.find_one({"nick":nick,"server":server})["online"]):
        a=ONLINES.find_one({"nick":nick,"server":server})["online"]
        a=a.replace("\'","\"")
        print(a)
    else:
        async with aiohttp.ClientSession() as sess:
            header = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
            a = await sess.get("https://berdoff.ru/getonline",data={"token": token_berdoff, "nick": nick,"server":server})
            a= await a.text()
            
            if ONLINES.count_documents({"nick":nick,"server":server})!=0:
                ONLINES.delete_one({"nick":nick,"server":server})
                ONLINES.insert_one({"nick":nick,"online":str(a),"server":server})
            else:
                ONLINES.insert_one({"nick":nick,"online":str(a),"server":server})
    online = json.loads(a)
    reps=bool(online["reports"]["check"])
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

    async with aiohttp.ClientSession() as sess:
        nick = await sess.get(f"https://seraphtech.site/api/v2/forum.getAdmins?vk={id_authora}&token={token_seraph}&server=21",timeout=5)
        nick= await nick.text()
        nick = json.loads(nick)
    if len(nick["response"]) == 0:
        await message.answer(f"Вы не являетесь администратором")
    else:
        nick=nick["response"][0]["nick"]
        await message.answer(f"⌛ Идет загрузка информации для выдачи Аццепт-кода!")
        code=get_code(nick)
        xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
        if code!="bad":
            code_time = code.split()[1]
            code=code.split()[0]
            async with aiohttp.ClientSession() as sess:
                logs=await sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=login&sort=desc&player={nick}&limit=1000",headers=header,cookies=json.loads(xsrf))
                logs= await logs.text()
            logs = BeautifulSoup(logs, "lxml")
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




@bot.on.message(text="!ацепт <nick>")
async def accept(message: Message,nick: Optional[str] = None):
    global sess
    users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id
    if str(id_authora)=="-212957523":
        async with aiohttp.ClientSession() as sess:
            header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
            xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
            nick = await sess.get(f"https://seraphtech.site/api/v2/forum.getAdmins?nick={nick}&token={token_seraph}&server=21",timeout=5)
            nick= await nick.text()
            nick = json.loads(nick)
            if len(nick["response"]) == 0:
                await message.answer(f"Вы не являетесь администратором")
            else:
                id_vk=nick["response"][0]["vk"]
                nick=nick["response"][0]["nick"]
                
                await message.answer(f"⌛ Идет загрузка информации для выдачи Аццепт-кода!")
                code=get_code(nick)
                if code!="bad":
                    code_time = code.split()[1]
                    code=code.split()[0]
                    logs=await sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=login&sort=desc&player={nick}&limit=1000",headers=header,cookies=json.loads(xsrf))
                    logs= await logs.text()
                    logs = BeautifulSoup(logs, "lxml")
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
                    ans_msg=f"""@id{id_vk}({nick}) запрашивает Accept!

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
                    forms.insert_one({"forma":f"/a {nick} новый ацепт код не найден!","author":id_authora,"status":0})
                    await message.answer(f"""Новый accept-code не найден!

        1) Напишите в игре /qaccadmin
        2) Выберите ник "Rafael_Camilleri"
        3) Через 15 секунд повторите попытку !ацепт""")


@bot.on.message(text="/id_be")
async def hi_handler(message: Message):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.reply_message.from_id
    await message.answer(f"{message.chat_id}")

@bot.on.message(text=["/ip","/ip <ip1> <ip2>","/ip <ip1>"])
async def get_info_ip(message: Message,ip1: Optional[str] = None,ip2: Optional[str] = None):
    ans=""
    if ip1 is not None:
        ip1=testip.get_info_by_ip(ip1)
        ans+="🌍 Информация о "+ip1["ip"]+" 📝\n🗺 Страна - "+ip1["country"]+"\n📍 Город - "+ip1["city"]+"\n🌌 Регион - "+ip1["region"]+"\n🌐 Провайдер - "+ip1["org"]+"\n🕒 Часовой Пояс - "+ip1["timezone"]
        if ip2 is not None:
            ip2=testip.get_info_by_ip(ip2)
            ans+="\n\n🌍 Информация о "+ip2["ip"]+" 📝\n🗺 Страна - "+ip2["country"]+"\n📍 Город - "+ip2["city"]+"\n🌌 Регион - "+ip2["region"]+"\n🌐 Провайдер - "+ip2["org"]+"\n🕒 Часовой Пояс - "+ip2["timezone"]
            ans+="\n\n🚄 Расстояние между ип: "+str(testip.get_distance_between_coord(ip1["loc"],ip2["loc"]))+" км"
        await message.answer(ans)
            
    else:
        await message.answer("❗ Используйте /ip [ip1] или /ip [ip1] [ip2]")


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


@bot.on.message(text=["/kfadd <dostup>","/kfadd"])
async def kfadd(message: Message,dostup: Optional[str] = None):
    id_authora=str(message.from_id)
    kf=str(message.chat_id)
    if str(id_authora)=="178391887":
        if dostup is not None:
            if forms.count_documents({"kf":kf})!=0:
                forms.update_one({"kf":kf},{"$set":{"dostup":dostup}})
            else:
                forms.insert_one({"kf":kf,"dostup":dostup})
            await message.answer(f"Значение для беседы {kf} успешно изменено на {dostup}")
        else:
            await message.answer("Используйте /kfadd [0/1]")

@bot.on.message(text=["/logs <nick> <server>","/logs","/logs <nick>"])
async def log(message: Message,nick: Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if (server!=None and (str(message.chat_id)=="3" or str(message.chat_id)=="13")) or (server!=None and str(id_authora)=="178391887"):
        pass
    else:
        server="21"   
    if forms.count_documents({"kf":str(message.chat_id)})!=0:
        dostup=forms.find_one({"kf":str(message.chat_id)})["dostup"]
    else:
        dostup="0"
    print(dostup)
    if dostup=="1" or str(id_authora)=="178391887":
        if nick!=None:
            await message.answer("Началась загрузка "+servers[server]+", примерное время загрузки 30 секунд")
            async with aiohttp.ClientSession() as sess:
                a = await sess.get("https://berdoff.ru/loadlogsdawdawdwadwadwadwadwa2121",data={"token": token_berdoff, "nick": nick,"server":server})
                a = await a.text()
            await message.answer(f"Загружен лог на 7 дней\nhttps://berdoff.ru/getlogs?token={a}")
        else:
            await message.answer("Используйте /logs [id/nick]")

@bot.on.message(text=["/delban <fforms> <ttype>"])
async def delban(message: Message,fforms: Optional[str] = None,ttype: Optional[str] = None):
    server=fforms.split("[")[1].split("]")[0]
    nick=fforms.split("]")[1].strip()
    if ttype=="баг":
        forms.update_one({"type":"vc_bans","server":server},{"$set":{"server":forms.find_one({"type":"vc_bans"}[server]).replace(f"/banoff 0 {nick} 2000 Багоюз // Рой\n","")}})
    await message.answer(f"Игрок {fforms} успешно удален из списка банов")




@bot.on.message(text=["/cc <nick> <server>"])
async def cc(message: Message,nick: Optional[str] = None,server: Optional[str] = None):
    xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
    async with aiohttp.ClientSession() as sess:
        k=1
        bans=""
        await message.answer("Start")
        
        logs= await sess.get(url=f"https://arizonarp.logsparser.info/?server_number=201&type%5B%5D=inventory_add&sort=desc&dynamic%5B26%5D=4608&page={k}&limit=1000&player=%5B{server}%5D{nick}",headers=header,cookies=json.loads(xsrf))
        logs=await logs.text()
        while not "Показано с 0 из" in logs:
            logs=BeautifulSoup(logs,"lxml")
            stroki=logs.find_all("tr")[1:]
            for i in stroki:
                await message.answer(i.text)
                if "-" in i.text.split("в количестве")[1].split(",")[0]: 
                    vc_money=i.find_all("div",class_="app__hidden")[0].find_all("li")[1].find("code").text
                    bans+=" ".join(i.text.split("I:")[0].strip().split())+f" (VC: {vc_money}$)"
            k+=1
            logs= await sess.get(url=f"https://arizonarp.logsparser.info/?server_number=201&type%5B%5D=inventory_add&sort=desc&dynamic%5B26%5D=4608&page={k}&limit=1000&player=%5B{server}%5D{nick}",headers=header,cookies=json.loads(xsrf))
            logs=await logs.text()
        await message.answer(bans)
        


@bot.on.message(text=["/vigruz <start> <end>"])
async def vigruz(message: Message,start: Optional[str] = None,end: Optional[str] = None):
    xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
    async with aiohttp.ClientSession() as sess:
        a = await sess.get("https://arizonarp.logsparser.info/",headers=header,cookies=json.loads(xsrf))
        if "Queen-Creek" in await a.text():
            await message.answer("Начинаю выгрузку")
            k=1
            for k in range(int(start),int(end)):
                logs= await sess.get(url=f"https://arizonarp.logsparser.info/?server_number=201&type%5B%5D=inventory_add&sort=desc&dynamic%5B26%5D=4608&page={k}&limit=1000")
                logs = BeautifulSoup(await logs.text(), "lxml")
                stroki = logs.find_all("tr")[1:]
                for i in stroki:
                    if "-" in i.text.split("в количестве")[1].split(",")[0]:
                        fforms=i.text.split()[3]
                        server=fforms.split("[")[1].split("]")[0]
                        nick=fforms.split("]")[1].strip()
                        if nick not in forms.find_one({"type":"vc_bans"})[server]:
                            forms.update_one({"type":"vc_bans"},{"$set":{server:forms.find_one({"type":"vc_bans"})[server]+f"/banoff 0 {nick} 2000 Багоюз // Рой\n"}})
                            forms.update_one({"type":"docs"},{"$set":{"docs":forms.find_one({"type":"docs"})["docs"]+"\n"+" ".join(i.text.split("I:")[0].strip().split())}})
                            await message.answer(f"Форма /banoff 0 {nick} 2000 Багоюз // Рой S[{server}] успешно записана")
                await message.answer(f"Выгружена страница номер {k}")


@bot.on.message(text=["/mlogs <nick> <server>","/mlogs","/mlogs <nick>"])
async def log(message: Message,nick: Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if (server!=None and (str(message.chat_id)=="3" or str(message.chat_id)=="13")) or (server!=None and str(id_authora)=="178391887"):
        pass
    else:
        server="21"   
    if forms.count_documents({"kf":str(message.chat_id)})!=0:
        dostup=forms.find_one({"kf":str(message.chat_id)})["dostup"]
    else:
        dostup="0"
    if dostup=="1" or str(id_authora)=="178391887":
        if nick!=None:
            await message.answer("Началась загрузка "+servers[server]+", примерное время загрузки 5 минут")
            async with aiohttp.ClientSession() as sess:
                a = await sess.get("https://berdoff.ru/loadlogsdawdawdwadwadwadwadwa212132222",data={"token": token_berdoff, "nick": nick,"server":server})
                a = await a.text()
            await message.answer(f"Загружен лог на 30 дней\nhttps://berdoff.ru/getlogs?token={a}")
        else:
            await message.answer("Используйте /mlogs [id/nick]")


@bot.on.message(text=["/flogs <nick> <server>","/flogs","/mlogs <nick>"])
async def fulllog(message: Message,nick: Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if (server!=None and (str(message.chat_id)=="3" or str(message.chat_id)=="13")) or (server!=None and str(id_authora)=="178391887"):
        pass
    else:
        server="21"   
    if forms.count_documents({"kf":str(message.chat_id)})!=0:
        dostup=forms.find_one({"kf":str(message.chat_id)})["dostup"]
    else:
        dostup="0"
    if dostup=="1" or str(id_authora)=="178391887":
        if nick!=None:
            await message.answer("Началась загрузка "+servers[server]+", примерное время загрузки 10 минут")
            async with aiohttp.ClientSession() as sess:
                a = await sess.get("https://berdoff.ru/api/loadfulllog",data={"token": token_berdoff, "nick": nick,"server":server},timeout=3600)
                await message.answer(f"Загружен лог за всё время дней\nhttps://berdoff.ru/getlogs?token="+await a.text())
        else:
            await message.answer("Используйте /flogs [id/nick]")


@bot.on.message(text=["/ac <monday>","/ac"])
async def acc(message: Message,monday: Optional[str] = None):
    if str(message.chat_id=="3"):
        if monday is not None:
            accs=forms.find_one({"type":"accepts","monday":monday})["accepts"]
            accs=accs.replace("\'","\"")
            accs=json.loads(accs)
            ans=f"Статистика по ацептам за неделю с {monday}\n\n"
            for i in accs:
                name=await bot.api.users.get(i)
                #await bot.api.messages.send(chat_id=3, message=str(name[0]), random_id=0,disable_mentions=1)
                name=name[0].first_name+" "+name[0].last_name
                ans+="@id"+i+f"({name}): "+str(accs[i])+" accepts\n"
            await bot.api.messages.send(chat_id=3, message=ans, random_id=0,disable_mentions=1)
            
@bot.on.message(text=["/stats"])
async def stats(message: Message):
    if str(message.chat_id=="12"):
        id_authora=str(message.from_id)
        user=loggs.find_one({"type":"family","id_owner":id_authora})
        id_leader=user["id_leader"]
        nick_leader=user["nick_leader"]
        leader=f"@id{id_leader}({nick_leader})"
        if id_leader=="":
            leader="Отсутсвует"
        if nick_leader=="":
            leader="Отсутсвует"
        
        await message.answer(f"Семья: "+user["family"]+"\n"+"Лидер семьи: @id"+user["id_owner"]+"("+user["nick"]+")\n"+"Фракция: "+user["frac"]+"\n"+f"Лидер фракции: {leader}\nНевыплаченный штраф: "+norm_money(user["dolg"])+"$")
    


@bot.on.message(text=["/addleader <tag> <nick>","/addleader"])
async def add_leader(message: Message,tag: Optional[str] = None,nick: Optional[str] = None):
    if str(message.chat_id=="12"):
        id_authora=str(message.from_id)
        if nick is not None:
            id_frac=loggs.find_one({"type":"family","id_owner":id_authora})["id_frac"]
            tag=get_id_by_tag(tag)
            frac=private_fracs[id_frac]
            loggs.update_one({"type":"family","id_owner":id_authora},{"$set":{"id_leader":tag,"nick_leader":nick}})
            await message.answer({f"Лидером организации {frac} назначен @id{tag}({nick})"})
        else:
            await message.answer("Используйте /addleader <tag> <nick>")


@bot.on.message(text=["/removeleader <nick>","/removeleader"])
async def add_leader(message: Message,nick: Optional[str] = None):
    if str(message.chat_id=="12"):
        id_authora=str(message.from_id)
        if nick is not None:
            id_frac=loggs.find_one({"type":"family","id_owner":id_authora})["id_frac"]
            tag=loggs.find_one({"type":"family","id_owner":id_authora})["id_leader"]
            frac=private_fracs[id_frac]
            loggs.update_one({"type":"family","id_owner":id_authora},{"$set":{"id_leader":"","nick_leader":""}})
            await message.answer({f"C Лидерки организации {frac} снят @id{tag}({nick})"})
        else:
            await message.answer("Используйте /removeleader <nick>")


@bot.on.message(text=["/addfam <tag> <nick> <family> <id_frac>","/addfam"])
async def add_fam(message: Message,tag: Optional[str] = None,nick: Optional[str] = None,family: Optional[str] = None,id_frac: Optional[str] = None):
    if str(message.chat_id=="3"):
        if id_frac is not None:
            tag=get_id_by_tag(tag)
            frac=private_fracs[id_frac]
            if loggs.count_documents({"family":family})==0:
                loggs.insert_one({"type":"family","id_owner":tag,"nick":nick,"family":family,"id_frac":id_frac,"frac":frac,"dolg":0,"nick_leader":"","id_leader":""})
                await message.answer({f"Семья {family} успешно добавлена. Фракция: {frac}. Владелец @id{tag}({nick})"})
            else:
                await message.answer("Ошибка. Данная семья уже добавлена!")
        else:
            await message.answer("Используйте /addfam <tag> <nick> <family> <id_frac>")

@bot.on.message(text=["/tagfrac"])
async def tagfrac(message: Message):
    await message.answer("""🔍Страховая компания »»» 28
🔍Больница Джефферсон »»» 201
🔍Radio LV »»» 24
🔍Radio SF »»» 26
🔍Больница SF »»» 8
🔍La Cosa Nostra »»» 18
🔍Night Wolfs »»» 25
🔍Tierra Robada Bikers »»» 101""")

@bot.on.message(text=["/pr <fforms> <docs>","/pr <fforms>"])
async def pr_vc(message: Message,fforms: Optional[str] = None,docs: Optional[str] = None):
    server=fforms.split("[")[1].split("]")[0]
    nick=fforms.split("]")[1].strip()
    if nick in forms.find_one({"type":"vc_bans"})[server]:
        await message.answer(f"Форма /banoff 0 {nick} 2000 Продажа вирт // Раф S[{server}] уже записана")
    else:
        forms.update_one({"type":"vc_bans"},{"$set":{server:forms.find_one({"type":"vc_bans"})[server]+f"/banoff 0 {nick} 2000 Продажа вирт // Раф\n"}})
        if docs!=None:
            forms.update_one({"type":"docs"},{"$set":{"docs":forms.find_one({"type":"docs"})["docs"]+"\n"+docs}})
        await message.answer(f"Форма /banoff 0 {nick} 2000 Продажа вирт // Раф S[{server}] успешно записана")

@bot.on.message(text=["/po <fforms> <docs>","/po <fforms>"])
async def po_vc(message: Message,fforms: Optional[str] = None,docs: Optional[str] = None):
    server=fforms.split("[")[1].split("]")[0]
    nick=fforms.split("]")[1].strip()
    if nick in forms.find_one({"type":"vc_bans"})[server]:
        await message.answer(f"Форма /banoff 0 {nick} 2000 Покупка вирт // Раф S[{server}] уже записана")
    else:
        forms.update_one({"type":"vc_bans"},{"$set":{server:forms.find_one({"type":"vc_bans"})[server]+f"/banoff 0 {nick} 2000 Покупка вирт // Раф\n"}})
        if docs!=None:
            forms.update_one({"type":"docs"},{"$set":{"docs":forms.find_one({"type":"docs"})["docs"]+"\n"+docs}})
        await message.answer(f"Форма /banoff 0 {nick} 2000 Покупка вирт // Раф S[{server}] успешно записана")


@bot.on.message(text=["/vz <fforms> <docs>","/vz <fforms>"])
async def po_vc(message: Message,fforms: Optional[str] = None,docs: Optional[str] = None):
    server=fforms.split("[")[1].split("]")[0]
    nick=fforms.split("]")[1].strip()
    if nick in forms.find_one({"type":"vc_bans"})[server]:
        await message.answer(f"Форма /banoff 0 {nick} 2000 Взломан // Раф S[{server}] уже записана")
    else:
        forms.update_one({"type":"vc_bans"},{"$set":{server:forms.find_one({"type":"vc_bans"})[server]+f"/banoff 0 {nick} 2000 Взломан // Раф\n"}})
        if docs!=None:
            forms.update_one({"type":"docs"},{"$set":{"docs":forms.find_one({"type":"docs"})["docs"]+"\n"+docs}})
        await message.answer(f"Форма /banoff 0 {nick} 2000 Взломан // Раф S[{server}] успешно записана")

@bot.on.message(text=["/docs <nick>"])
async def get_docs(message: Message,nick: Optional[str] = None):
    ans=""
    for i in forms.find_one({"type":"docs"})["docs"].split("\n"):
        if nick in i:
            ans+=i+"\n"
    await message.answer(ans)

@bot.on.message(text=["/clr"])
async def clr_bans(message: Message,fforms: Optional[str] = None):
    forms.delete_one({"type":"vc_bans"})
    forms.insert_one({"type":"vc_bans","01":"01: @akutaq \n\n","02":"02: @id321768809\n\n","03":"03: @jubileeprins\n\n","04": "04: @morozandre @ivankova1ev\n\n","05": "05: @s_disney\n\n","06":"06: @didiiiika\n\n","07":"07: @omorfik\n\n","08":"08: @royshelby @escobaronelove\n\n","09":"09: @yumatoren\n\n","10":"10: @ren_c_c \n\n","11":"11: @deathstroke41\n\n","12":"12: @faevg\n\n","13":"13: @team161team\n\n","14":"14:  @estenyolo\n\n","15":"15: @id41389036\n\n","16":"16: \n\n","17":"17: @filipp101 @cooper_x\n\n","18":"18: @alvares_serg @minatogrande\n\n","19":"19: @darkeepa @ferdikdesp\n\n","20":"20: @chikimony\n\n","21":"21: \n\n","22":"22: @legendprof\n\n","23":"23: @id204728630\n\n"})
    await message.answer("Таблица банов успешно обнулена")

@bot.on.message(text=["/bans"])
async def bans(message: Message,fforms: Optional[str] = None):
    ans=""
    for i in range(1,24):
        if len(str(i))==1:
            server="0"+str(i)
        else:
            server=str(i)
        formi=forms.find_one({"type":"vc_bans"})[server]
        if "/banoff" in formi:
            ans+="\n"+formi
    await message.answer(ans)

@bot.on.message(text=["/reload"])
async def game_forms(message: Message):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if str(message.chat_id)=="3":
        loggs.update_one({"type":"update"},{"$set":{"status":1}})
        await message.answer("Ожидайте перезапуска в течение 5 минут")

@bot.on.message(text=["/listdostup"])
async def listdostup(message: Message):
    if str(message.chat_id=="3"):
        accs=forms.find({"dostup":"1"})
        ans=f"Доступы у следующих людей\n\n"
        for i in accs:
            try:
                #await message.answer(i["user"])
                name=await bot.api.users.get(int(i["user"]))
                name=name[0].first_name+" "+name[0].last_name
                ans+="@id"+i["user"]+f"({name})\n"
            except:
                pass
            
            #await bot.api.messages.send(chat_id=3, message=str(name[0]), random_id=0,disable_mentions=1)
           
        await bot.api.messages.send(chat_id=3, message=ans, random_id=0,disable_mentions=1)

@bot.on.message(text=["/svrnt"])
async def serverstats(message: Message):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if str(message.chat_id)=="3":
        await message.answer("Обновление информации займет примерно 15 секунд")
        forms.insert_one({"forma":"/svrnt","author":id_authora,"status":0})
        await asyncio.sleep(15)
        await message.answer(forms.find_one({"type":"data"})["svrnt"])

@bot.on.message(text=["/game <fforms>"])
async def game_forms(message: Message,fforms: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if str(message.chat_id)=="3":
        if forms.count_documents({"user":id_authora})!=0:
            if forms.find_one({"user":id_authora})["dostup"]=="1":
                forms_bd=db["forms"]
                xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
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
                    date=date-datetime.timedelta(minutes=2)
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
                    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Atom/13.0.0.44 Safari/537.36'}
                    xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
                    async with aiohttp.ClientSession() as sess:
                        await message.answer("20")
                        logs=await sess.get(f"https://arizonarp.logsparser.info/?server_number=21&sort=desc&min_period={year}-{month}-{day}+{hour}%3A{minute}%3A00&player=QueenBot",headers=header,cookies=json.loads(xsrf))
                        logs=await logs.text()
                        logs=BeautifulSoup(logs,"lxml")
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




@bot.on.message(text=["/slet <code>","/slet"])
async def slet_text(message: Message,code: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if str(message.chat_id)=="9":
        if code is not None:
            forms_bd=db["forms"]
            forms_bd.insert_one({"forma":f"/a /slet_text {code}","author":id_authora,"status":0})
            try:
                slets_bd.delete_one({"code":code})
                await message.answer(f"Запись с кодом {code} удалена из бд")
            except:
                pass
            await message.answer(f"Текст с кодом {code} будет удален в течение 30 секунд")
        else:
            await message.answer("⛔Используйте /slet [code]")


@bot.on.message(text=["/chet <fps> <first> <second> <third> <fourth> <fifth> <close>","/chet"])
async def slet_chet(message: Message,fps: Optional[str] = None,first: Optional[str] = None,second: Optional[str] = None,third: Optional[str] = None,fourth: Optional[str] = None,fifth: Optional[str] = None,close: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    if close is not None:
        fps_count=fps
        fps=1/int(fps)
        fps_f=format(int(first)*fps,".3f")
        fps_s=format((int(second)-int(first))*fps,".3f")
        fps_t=format((int(third)-int(second))*fps,".3f")
        fps_fo=format((int(fourth)-int(third))*fps,".3f")
        fps_fi=format((int(fifth)-int(fourth))*fps,".3f")
        fps_cl=format((int(close)-int(fifth))*fps,".3f")
        full=format(float(fps_f)+float(fps_s)+float(fps_t)+float(fps_fo)+float(fps_fi)+float(fps_cl),".3f")
        await message.answer(f"▶Кадров: {fps_count} fps\n▶Первый символ(кадр): {first} ({fps_f}s)\n▶Второй символ(кадр): {second} ({fps_s}s)\n▶Третий символ(кадр): {third} ({fps_t}s)\n▶Четвертый символ(кадр): {fourth} ({fps_fo}s)\n▶Пятый символ(кадр): {fifth} ({fps_fi}s)\n▶Закрытие капчи(кадр): {close} ({fps_cl}s)\nОбщее время: {full}s")
    else:
        await message.answer("⛔Используйте /chet [fps] [1 символ] [2 символ] [3 символ] [4 символ] [5 символ] [close]")

@bot.on.message(text=["/gform <fforms>","/gform"])
async def game_forms_slet(message: Message,fforms: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=str(message.from_id)
    xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
    if str(message.chat_id)=="9":
        if fforms is not None:
            forms_bd=db["forms"]
            xsrf=loggs.find_one({"type":"token"})["session"].replace("\'","\"")
            a=message.text.replace("/gform","").strip()
            a=a.split("\n")
            nicks=[]
            if len(a)>10:
                await message.answer("Не больше 10 форм!")
            else:
                for i in a:
                    if i.split()[0]=="/unjailoff":
                        nick=i.split()[1]
                        async with aiohttp.ClientSession() as sess:
                            logs=await sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=jail&sort=desc&player={nick}",headers=header,cookies=json.loads(xsrf))
                            logs=BeautifulSoup(await logs.text(),"lxml")
                        jail=logs.find_all("tr")[1]
                        if "опру" in jail.text.lower() or "опра" in jail.text.lower():
                            forms_bd.insert_one({"forma":i,"author":id_authora,"status":0})
                        else:
                            await message.answer(f"⛔Игрок {nick} не был посажен за опру")
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
                async with aiohttp.ClientSession() as sess:
                    logs=await sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=rmute&type%5B%5D=unrmute&type%5B%5D=agl&type%5B%5D=givedonate&type%5B%5D=ao_chat&type%5B%5D=ban&type%5B%5D=jail&type%5B%5D=mute&type%5B%5D=warn&type%5B%5D=banip&type%5B%5D=unban&type%5B%5D=unjail&type%5B%5D=unmute&type%5B%5D=unwarn&type%5B%5D=unbanip&type%5B%5D=unwarn_talon&type%5B%5D=inventory_admin&sort=desc&min_period={year}-{month}-{day}+{hour}%3A{minute}%3A00&player=QueenBot",headers=header,cookies=json.loads(xsrf))
                logs=BeautifulSoup(await logs.text(),"lxml")
                stroki=logs.find_all("tr")[1:]
                forms_plus=[]
                if len(stroki)!=0:
                    for i in stroki:
                        forms_plus.append(" ".join(i.text.split("I:")[0].strip().split()))
                await message.answer("Выданные в игре формы:\n\n"+"\n".join(forms_plus))
        else:
            await message.answer("⛔Используйте /gform [формы]")

        

@bot.on.message(text=["/onlines <lvl>"])
async def online(message: Message, lvl: Optional[str] = None):
    id_authora=str(message.from_id)
    if message.chat_id==5 and not id_authora=="37148810":
        on_ans=""
        server="21"
        lvl=lvl.strip()
        on_ans=f"""📝Statistic of admistrators {lvl}-х LVL for last week\n\n"""
        vremya_start=int(str(time.time()).split(".")[0])
        if "Statistic of admistrators" in on_ans:
            await message.answer("✅ Waiting")
            adms=[]
            async with aiohttp.ClientSession() as sess:
                a=await sess.get(f"https://seraphtech.site/api/v2/forum.getAdmins?&token={token_seraph}&server=21",timeout=5)
                a=await a.text()
                a=json.loads(a)["response"]
            
                for i in a:
                    if int(i["lvl"])<=int(lvl.split("-")[1]) and int(i["lvl"])>=int(lvl.split("-")[0]):
                        
                        onl=await get_online_lw(i["nick"], 1, i["nick"],"21")
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
                        time.sleep(1)
            #await message.answer(str(adms))
            k=1
            for i in sorted(adms,key=lambda k:(k["onl_int"],k["reports"]),reverse=True):
                on_ans+=f"[{k}]"+" "+i["nick"]+" ["+i["lvl"]+"] Play: "+i["online"]+" "+i["ch_onl"]+" Reps: "+str(i["reports"])+" "+i["ch_reps"]+"\n"
                k+=1
            await message.answer(on_ans)
            await message.answer("Время работы: "+str(int(str(time.time()).split(".")[0])-vremya_start)+" секунд")
                        


                




    


@bot.on.message(text=["/myonl","/myonline"])
async def myonline(message: Message):
    async with aiohttp.ClientSession() as sess:
        #users_info = await bot.api.users.get(message.from_id)
        id_authora=message.from_id
        nick = (await sess.get(
            f"https://seraphtech.site/api/v2/forum.getAdmins?vk={id_authora}&token={token_seraph}&server=21",timeout=5))
        nick=await nick.text()
        nick= json.loads(nick)
        if len(nick["response"]) == 0:
            await message.answer(f"❌  Вы не являетесь администратором")
        else:
            nick = nick["response"][0]["nick"]
            await message.answer(f"⚙ {nick} началась загрузка онлайна")
            online = await (get_online(nick, 1, nick,"21"))
            await message.answer(online)


@bot.on.message(text=["/online <nick> <server>","/onl <nick> <server>","/onl <nick>","/online <nick>","/onl","/online"])
async def online(message: Message, nick:Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.from_id
    if len(message.text.split())<4 and len(message.text.split())>1:
        if server is None:
            server="21"
        if server in servers:
            await message.answer(f"⚙ {nick} началась загрузка онлайна "+servers[server])
            online = await get_online(nick, 1, nick,server)
            await message.answer(online)
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("/onl [nick] [server(не обязательно)]")


@bot.on.message(text=["/monline <nick> <server>","/monl <nick> <server>","/monl <nick>","/omnline <nick>","/monl","/monline"])
async def monline(message: Message, nick:Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.from_id
    if len(message.text.split())<4 and len(message.text.split())>1:
        if server is None:
            server="21"
        if server in servers:
            await message.answer(f"⚙ {nick} началась загрузка онлайна "+servers[server])
            online = await get_online_month(nick, 1, nick,server)
            await message.answer(online)
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("/monl [nick] [server(не обязательно)]")

@bot.on.message(text=["/reports <days> <server>","/reports <days>","/reports"])
async def reports(message: Message,days:Optional[str] = None,server:Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    #id_authora=message.from_id
    if days:
        if server is None:
            server="21"
        if server in servers:
            await message.answer(f"⚙ началась загрузка репорта "+servers[server])
            online = await get_reports_month(server,days)
            await message.answer(online)
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("Используйте /reports <days> <server(по умолчанию 21)>")
    


@bot.on.message(text=["/shtraf <nick> <amount> <docs>","/shtraf"])
async def shtraf(message: Message, nick:Optional[str] = None, amount:Optional[str] = None, docs:Optional[str] = None):
    if message.chat_id==8:
        if nick and amount:
            user=loggs.find_one({"type":"family","nick":nick})
            loggs.update_one({"type":"family","nick":nick},{"$set":{"dolg":loggs.find_one({"type":"family","nick":nick})["dolg"]+int(amount)}})
            await message.answer("Фракции "+user["frac"]+f" был назначен штраф {amount}$")
            await bot.api.messages.send(chat_id=12,message="Фракции "+"@id"+user["id_leader"]+"("+user["frac"]+f") был назначен штраф {amount}$\nПричина: {docs}",random_id=0)
        else:
            await message.answer("Используйте /shtraf <nick> <amount> <docs>")

@bot.on.message(text=["/fams"])
async def fams(message: Message, nick:Optional[str] = None, amount:Optional[str] = None, docs:Optional[str] = None):
    users=loggs.find({"type":"family"})
    for i in users:
        await message.answer(f"Семья: "+i["family"]+"\n"+"Лидер семьи: @id"+i["id_owner"]+"("+i["nick"]+")\n"+"Фракция: "+i["frac"]+"\n"+f"Лидер фракции:"+"@id"+i["id_leader"]+"("+i["nick_leader"]+")\nНевыплаченный штраф: "+norm_money(i["dolg"])+"$")


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
            online = await get_online_lw(nick, 1, nick,server)
            await message.answer(online)
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("/lw_onl [nick] [server(не обязательно)]")


@bot.on.message(text=["/donl <nick> <server>","/donl"])
async def delonl(message: Message, nick: Optional[str] = None,server: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id
    if server and str(id_authora)=="178391887":
        if server in servers:
            ONLINES.delete_one({"nick":nick,"server":server})
            await message.answer("Онлайн пользователя "+nick+f"[{server}] успешно очищен")
        else:
            ans=""
            for i in servers:
                ans+=servers[i]+" -> "+i+'\n' 
            await message.answer(ans)
    else:
        await message.answer("/donl [nick] [server]")


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
                logs=sess.get(f"https://arizonarp.logsparser.info/?server_number={server}&type%5B%5D=login&type%5B%5D=disconnect&sort=desc&player={id_acc}&limit=1000")
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
                bban=""
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
        id_vk = json.loads(requests.get(f"https://seraphtech.site/api/v2/forum.getAdmins?nick="+event.object.payload["nick"]+f"&token={token_seraph}&server=21",timeout=5).text)["response"][0]["vk"]
        event.object.payload["vk"]=id_vk
        if str(event.object.user_id)==str(event.object.payload["vk"]):
            await bot.api.messages.send(chat_id=3, message=f'@id{event.object.user_id}(❌) Нельзя выдать ацепт самому себе!', random_id=0)
        else:
            await bot.api.messages.send(chat_id=3, message=f'@id{event.object.user_id}(☑) Ацепт код отправлен  @id'+str(event.object.payload["vk"])+"("+event.object.payload["nick"]+")", random_id=0)
           
            forms.insert_one({"forma":"/pm "+event.object.payload["nick"]+" 1 Ваш код: "+event.object.payload["code"],"author":event.object.user_id,"status":0})
            forms.insert_one({"forma":"/a "+event.object.payload["nick"]+" ваш код: "+event.object.payload["code"],"author":event.object.user_id,"status":0})
            
            
            await bot.api.messages.send(chat_id=2, message="@id"+str(event.object.payload["vk"])+"("+event.object.payload["nick"]+") "+" Ваш код: "+event.object.payload["code"]+"  | Коду: "+str(event.object.payload["time"])+"  минут",random_id=0)
            today = datetime.date.today()
            data_start = today - datetime.timedelta(days=today.weekday())
            data_start = str(data_start.day) + '.' + str(data_start.month) + '.' + str(data_start.year)
            if forms.count_documents({"type":"accepts","monday":data_start})==0:
                forms.insert_one({"type":"accepts","monday":data_start,"accepts":"{}"})
            accs=forms.find_one({"type":"accepts","monday":data_start})["accepts"]
            accs=accs.replace("\'","\"")
            accs=json.loads(accs)
            #await bot.api.messages.send(chat_id=3, message=str(accs),random_id=0)
            if str(event.object.user_id) not in accs:
                accs[str(event.object.user_id)]=1
            else:
                accs[str(event.object.user_id)]=int(accs[str(event.object.user_id)])+1
            forms.update_one({"type":"accepts","monday":data_start},{"$set":{"accepts":str(accs)}})
    elif event.object.payload["cmd"]=="ne accept":
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=ShowSnackbarEvent(text="‼ Ацепт код отказан ‼").json(),
        )
        await bot.api.messages.send(chat_id=2, message="@id"+str(event.object.payload["vk"])+"("+event.object.payload["nick"]+") "+" в выдаче кода отказано!",random_id=0)
        await bot.api.messages.send(chat_id=3,message='‼ Ацепт код отказан ‼\n✅ Сообщение об отказе ' + f'@id{event.object.user_id}(отправлено)',random_id=0)
        try:
            forms.insert_one({"forma":"/a "+event.object.payload["nick"]+" ваш ацепт отказан!","author":"bot","status":0})
        except:
            pass

bot.run_forever()
    






