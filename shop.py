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
from config import tok,mongo
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials

link = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']   # задаем ссылку на Гугл таблици
my_creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', link) #формируем данные для входа из нашего json файла
client = gspread.authorize(my_creds)    # запускаем клиент для связи с таблицами
sheet = client.open('#Queen Creek | Форумный магазин скинов (Ответы)').sheet1    # открываем нужную на таблицу и лист



cluster=MongoClient(mongo,tlsCAFile=certifi.where())
db=cluster["UsersData"]
collection=db["logs"]
xsrf=collection.find_one({"type":"token"})["session"]
sess=requests.session()
skins=db["skins"]
print(xsrf)
sess.cookies.update({"laravel_session":xsrf,"XSRF-TOKEN":xsrf})
warn_skins=["74","92","99","285"]

bot = Bot(token=tok)

@bot.on.message(text=["/shop"])
async def shop(message: Message):
    if message.chat_id==3:
        adms=["Lorenzo_Almas","Rafael_Camilleri","Ferdik_King","QueenBot","Oliver_Hemsworth"]
        id_authora=message.from_id
        i=2
        try:
            ss=""
            for i in skins.find({"check":"0"}):
                ss+="/agiveskinoff "+i["nick"]+" "+i["skin"]+"\n"
                skins.update_one({"i":i["i"]},{"$set":{"check":"1"}})
            await message.answer(ss)
        except:
            await message.answer("Невыданных форм нет")
        try:
            await message.answer("Загружаю новые")
            while str(sheet.cell(i,8).value)=="TRUE":
                #sheet.update_cell(i,8,False)
                i+=1
            skin=sheet.cell(i,5).value
            nick=sheet.cell(i,2).value
            perevods=""
            logs=sess.get(f"https://arizonarp.logsparser.info/?server_number=21&type%5B%5D=bank_give&sort=desc&player={nick}&limit=100")
            logs = BeautifulSoup(logs.text, "lxml")
            stroki = logs.find_all("tr")[1:5]
            for i1 in stroki:
                i1=" ".join(i1.text.split("I")[0].strip().split())
                if i1.split()[6] in adms:
                    perevods+=i1+"\n"
            ans_msg=f"Ник: {nick}\nСкин: {skin}\n"+"Скрины: \n"+sheet.cell(i,3).value+"\n"+sheet.cell(i,4).value+"\nVK:"+sheet.cell(i,6).value+f"\nПереводы: \n\n{perevods}"


            KEYBOARD = (
                            Keyboard(inline=True)
                                .add(Callback("Выдать", payload={"cmd": "giveskin","nick":nick,"vk":id_authora,"i":i,"nick":nick,"skin":skin}), color=KeyboardButtonColor.POSITIVE)
                                .get_json()
                        )
            if skin not in warn_skins:
                await bot.api.messages.send(chat_id=3,message=ans_msg,keyboard=KEYBOARD,random_id=0)
        except:
            await message.answer("Новых покупок не найдено")
        
        

        



@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def handle_message_event(event: GroupTypes.MessageEvent):
    # event_data parameter accepts three object types
    # "show_snackbar" type
    if event.object.payload["cmd"]=="giveskin":
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
            event_data=ShowSnackbarEvent(text="☑ Выдача скина записана").json(),
            payload=event.object.payload
        )
        
        if skins.count_documents({"i":event.object.payload["i"]})==0:
            skins.insert_one({"i":event.object.payload["i"],"skin":event.object.payload["skin"],"nick":event.object.payload["nick"],"check":"0"})
            await bot.api.messages.send(chat_id=3, message=f'@id{event.object.user_id}(☑) Скин записан', random_id=0)
            sheet.update_cell(event.object.payload["i"],8,True)
        else:
            await bot.api.messages.send(chat_id=3, message=f'@id{event.object.user_id}(☑) Скин уже находится в списке выдачи', random_id=0)
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