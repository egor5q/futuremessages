# -*- coding: utf-8 -*-
import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback

token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(token)


client=MongoClient(os.environ['database'])
db=client.futuremessages
users=db.users

symbols=['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
        'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

try:
    pass

except Exception as e:
    print('Ошибка:\n', traceback.format_exc())
    bot.send_message(441399484, traceback.format_exc())

@bot.message_handler()
def add(m):
    user=users.find_one({'id':m.from_user.id})
    if user==None:
        users.insert_one(createuser(m.from_user))
        user=users.find_one({'id':m.from_user.id})
    if m.text[:4]=='/add':
        users.update_one({'id':user['id']},{'$set':{'status':'adding'}})
        bot.send_message(m.chat.id, 'Напишите сообщение, которое я отправлю вам позже.')
    elif user['status']=='adding':
        msg=createmsg(user, m.text)
        users.update_one({'id':user['id']},{'$set':{'futuremsgs.'+msg['code']:msg}})
        users.update_one({'id':user['id']},{'$set':{'status':'addtime'}})
        users.update_one({'id':user['id']},{'$set':{'code':msg['code']}})
        bot.send_message(m.chat.id, 'Отлично! А теперь выберите, через сколько времени я пришлю это вам. Формат:\n1d2h3m33s'+
                         ' - бот пришлёт вам сообщение через 1 день, 2 часа, 3 минуты и 33 секунды.')
    elif user['status']=='addtime':
        try:
            days=int(m.text.split('d')[0])
            m.text=m.text.split('d')[1]
        except:
            days=None
            bot.send_message(441399484, traceback.format_exc())
        try:
            hours=int(m.text.split('h')[0])
            m.text=m.text.split('h')[1]
        except:
            hours=None
            bot.send_message(441399484, traceback.format_exc())
        try:
            minutes=int(m.text.split('m')[0])
            m.text=m.text.split('m')[1]
        except:
            minutes=None
            bot.send_message(441399484, traceback.format_exc())
        try:
            secs=int(m.text.split('s')[0])
        except:
            secs=None
            bot.send_message(441399484, traceback.format_exc())
        ftime=time.time()+3*3600
        ctime=ftime
        text=''
        if days!=None:
            ftime+=days*86400
            text+=str(days)+' дней, '
        if hours!=None:
            ftime+=hours*3600
            text+=str(hours)+' часов, '
        if minutes!=None:
            ftime+=minutes*60
            text+=str(minutes)+' минут, '
        if secs!=None:
            ftime+=secs
            text+=str(secs)+' секунд, '
        if ftime!=ctime:
            text=text[:len(text)-2]
            text+='.'
            users.update_one({'id':user['id']},{'$set':{'futuremsgs.'+user['code']+'.time':ftime}})
            bot.send_message(m.chat.id, 'Вы успешно установили отправку сообщения! Вы получите его через '+text)
            users.update_one({'id':user['id']},{'$set':{'status':'free', 'code':None}})
            
        
        
        
def createmsg(user, msg):
    code=createcode(user)
    return {
        'code':code,
        'msg':msg,
        'time':None,
    }
                                                    
                                                    
def createcode(user):
    i=0
    ltrs=3
    code=''
    while i<ltrs:
        code+=random.choice(symbols)
        i+=1
    while code in user['futuremsgs']:
        code=''
        i=0
        while i<ltrs:
            code+=random.choice(symbols)
            i+=1
    return code
        
    
    
def createuser(user):
    return {
        'id':user.id,
        'futuremsgs':{},
        'name':user.first_name,
        'status':'free',
        'code':None
    }
    
    
def timecheck():
    globaltime=time.time()+3*3600
    for ids in users.find({}):
        user=ids
        for idss in user['futuremsgs']:
            try:
                if user['futuremsgs'][idss]['time']<=globaltime:
                    bot.send_message(user['id'], user['futuremsgs'][idss]['msg'])
                    users.update_one({'id':user['id']},{'$unset':{'futuremsgs.'+idss:1}})
            except:
                pass
    t=threading.Timer(3, timecheck)
    t.start()


    
timecheck()  
print('7777')
bot.polling(none_stop=True,timeout=600)

