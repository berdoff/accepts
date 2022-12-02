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
from config import tokr,mongo
import email


print(3)
cluster=MongoClient(mongo,tlsCAFile=certifi.where())
db=cluster["UsersData"]
collection=db["logs"]
rakbots_dostup=db["RAKBOT_DOSTUP"]
rakbots_bd=db["RAKBOT"]
print(4)





bot = Bot(token=tokr)








@bot.on.message(text=["/r <ip>"])
async def play_bot(message: Message, ip: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id
    if ip is not None and ip.count(".")==3 and ip!="":
        if rakbots_dostup.count_documents({"vk":str(id_authora)})!=0:
            user=rakbots_dostup.find_one({"vk":str(id_authora)})
            nick=user["nick"]
            ip=ip.strip()
            requests.get("http://berdoff.ru/api/addrakbot",data={"nick":user["nick"],"vk":user["vk"],"ip": ip})
            await message.answer(f"{nick}\nНачинаю снимать ракбота")
        else:
            await message.answer("Остутствует доступ, обратитесь к одному из них: \n\n @id307732925\n@id234150943\n@id163727821\n@id385588249\n@id632696170\n")
    else:
        await message.answer("Для снятия ракбота используйте /r [ваш ip]\n\nВзять можно с сайта https://2ip.ru")


@bot.on.message(text=["/rdostup"])
async def online(message: Message, ip: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    dostups="✅Доступ к снятию ракбота у следующих игроков:\n\n"
    for i in rakbots_dostup.find():
        dostups+="✏ @id"+i["vk"]+"("+i["nick"]+")\n"
    await message.answer(dostups)

@bot.on.message(text=["/stop"])
async def stop_bot(message: Message, ip: Optional[str] = None):
    #users_info = await bot.api.users.get(message.from_id)
    id_authora=message.from_id
    if rakbots_bd.count_documents({"vk":str(id_authora)})!=0:
        rakbots_bd.delete_many({"vk":str(id_authora)})
        await message.answer("Снятие ракбота остановлено")
    else:
        await message.answer("В данный момент ракбот не снимается")

bot.run_forever()
    






