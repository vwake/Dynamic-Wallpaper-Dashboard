import os
import sys
import ctypes
import arrow
import logging 
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from tinydb import TinyDB, Query, where
from datetime import datetime

ABSPATH = os.path.abspath(__file__)
CWD = os.path.dirname(ABSPATH)
os.chdir(CWD)

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
arrow_now = arrow.now().for_json()

wallpaper_path = r'C:\Users\vivek.ravindran\Desktop\SideProject\red.jpg'
text_color = (255, 255, 0)
background_color = (13, 2, 8)
width = (1360, 768)
font_size = 15
todos = []
font_color = (255, 255, 0)
box_color = (87, 232, 107)

db = TinyDB('db.json')

table = db.table('todos')
followup = db.table('followups')
timer = db.table('timer')

font = 'fonts/whitrabt.ttf'
Timer_font = 'fonts/Minalis Double Demo.otf'
Timer_font_size = 55

img = Image.new('RGB', width, color=background_color ) 
fnt = ImageFont.truetype(font, font_size)
timerfont = ImageFont.truetype(Timer_font, Timer_font_size)
d = ImageDraw.Draw(img)
w, h = 1360, 768 #Get system resolutions

shape = [(0, h), (w - 1170,  h - 180)] 
d.rectangle(shape, fill=background_color, outline=font_color)

arg = sys.argv
filename = arg[0]

def differhuman(starttime, endtime):
    # print("Fucnction differhuman")
    # print("***************************************************")
    # print(starttime)
    # print(endtime)
    diff =  arrow.get(starttime)  - arrow.get(endtime)
    days = diff.days # Get Day 
    hours,remainder = divmod(diff.seconds,3600) # Get Hour
    minutes,seconds = divmod(remainder,60) # Get Minute & Second 
    past = arrow.utcnow().shift(days=-days, hours=-hours, minutes=-minutes, seconds=-seconds )
    humantime = past.humanize(only_distance=True)
    # print("***************************************************")
    return humantime

def redraw():
    print("Redraw Function called")
    Todo = Query()
    todolist = table.search(Todo.status == 'pending')

    Followup = Query()
    followuplist = followup.search(Followup.status == 'pending')

    off = 20
    offset = 0
    d.text((0, 0), "Must Finish Today! :", font=fnt, fill=font_color)

    present = arrow.get(arrow_now)
    future = present.shift(hours=9) 

    # time_left_string = "Finish work " + test
    last_updated = "Last Updated :- " + dt_string
    daily_tasks_tile = "Daily Task"
    todays_followups = "Todays Follow ups"
    bar = "--------------"
    daily_task_list = ["Test Task 1", "Test Task 2",  "Test Task 3", "Test Task 4"]
    
    d.text((1000, h-50), last_updated, font=fnt, fill=font_color)
    
    d.text((1000, h-300), todays_followups, font=fnt, fill=font_color)
    
    d.text((50,  h - 160), daily_tasks_tile, font=fnt, fill=font_color)
    d.text((30, h - 140), bar, font=fnt, fill=font_color)
    d.text((30, h - 180), bar, font=fnt, fill=font_color)

    daily_task_display_offset = h - 150
    daily_off = 20

    followup_list_display_offset = h-300
    followup_offset = 20
    offset = 0

    timer_data = timer.all()
    print(timer_data)
    for startworktime in timer_data:
        print(startworktime['timestamp'])
        test_arrow = arrow.get(startworktime['timestamp'])
        print(test_arrow)
        workend = test_arrow.shift(hours=+12)
        time_left_string = "Focus!! Only " + workend.humanize(only_distance=True, granularity=["hour", "minute"]) + " Left!"
        time_left_string = workend.humanize(only_distance=True, granularity=["hour", "minute"])

        d.text((600, 10), time_left_string, font=timerfont, fill=font_color)

    for followupitem in followuplist:
        # print(followupitem)
        # print(followupitem['todo'])
        item = str(followupitem['todo'])
        f_timestamp = followupitem['timestamp']
        humantime = differhuman(arrow_now, f_timestamp)

        followup_list_display_offset += followup_offset
        display_followup = item  + " - " + humantime
        d.text((1000, followup_list_display_offset), display_followup, font=fnt, fill=font_color)

    for daily_task in daily_task_list:
        # print(daily_task)
        daily_task_display_offset += daily_off
        d.text((10, daily_task_display_offset), daily_task, font=fnt, fill=font_color)

    for item in todolist:

        summary = item['todo']
        i = item['int']
        # status = item['status']
        times = item['timestamp']  
        savedAt = arrow.get(times)
        humantime = differhuman(savedAt , arrow_now)
        todo = str(i) + " " + humantime + " " + summary

        offset += off + 1
        print(todo)
        d.text((10, offset), todo, font=fnt, fill=text_color)

    img.save(wallpaper_path)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)

def addEntry(newentry):
    data = table.all()
    index = len(data)
    table.insert({'int' : index, 'timestamp' : arrow_now,  'todo': newentry, 'status': 'pending'})

def delEntry(itr):
    print("LOG")
    del_index = int(itr[0])
    dTodo = Query()
    table.update({'status': 'Done'}, dTodo.int == del_index)

def input_todo(arg):
    print(arg)
    pass
    if len(arg) <  1:
        clean = arg
    elif len(arg) > 0:
        arg.remove(arg[0])
        arg.remove(arg[0])
        clean = arg
    else :
        print("do nothing")
    return clean

def addFollowup(item):
    print(item)
    followup_data = followup.all()
    index = len(followup_data)
    followup.insert({'int' : index, 'timestamp' : arrow_now,  'todo': item, 'status': 'pending'})

def reset():
    print("Reset Function called")
    table.purge()
    followup.purge()
    timer.purge()

def save():
    print("save function called")
    stopwork()
    filename = now.strftime("%b-%d-%Y")
    filename_ext = "data/" +filename + ".txt"
    f_save = open(filename_ext,"w+")
    todolist = table.all()
    timer_data = timer.all()
    followup_data = followup.all()
    print(todolist)
    f_save.write("TIMER" + '\n')
    f_save.write("-------------------------------------------------------------" + '\n')
    
    for times in timer_data:
        f_save.write( times['timestamp'] +" - " +  times['action'] + '\n')
    f_save.write("-------------------------------------------------------------" + '\n')
    for item in todolist:
        f_save.write( item['status'] +" - " +  item['todo'] + '\n')
    f_save.write("-------------------------------------------------------------" + '\n')
    for followup_item in followup_data:
        f_save.write( followup_item['status'] +" - " +  followup_item['todo'] + '\n')

    f_save.close()
    reset()
    redraw()

def startwork():
    timer.purge()
    timer_data = timer.all()
    index = len(timer_data)
    print("startwork called")
    timer.insert({'int' : index, 'timestamp' : arrow_now, 'action' : 'Started Work'})

        # print(startworktime['timestamp'])

def stopwork():
    timer_data = timer.all()
    index = len(timer_data)
    timer.insert({'int' : index, 'timestamp' : arrow_now, 'action' : 'Stop Work'})


if len(arg) > 1:
    action = arg[1]
    print(action)
    print("************************************************")
    if action == "a" :
        print("Add Todos", action)
        todo_item = input_todo(arg)
        newentry = ' '.join(word for word in todo_item)
        addEntry(newentry)
        redraw()
    elif action == "d":
        print("Delete Todos", action)
        # print(arg)
        todo_item = input_todo(arg)
        delEntry(todo_item)
        redraw()
    elif action == "save":
        print("Save action", action)
        # print(arg)
        # todo_item = input_todo(arg)
        save()
        # redraw()
    elif action == "f":
        print("Create Follow up", action)
        # print(arg)
        todo_item = input_todo(arg)
        newfollowup = ' '.join(word for word in todo_item)
        addFollowup(newfollowup)
        redraw() ,
        
    elif action == "r":
        print("Reset Todos", action)
        redraw()

    elif action == "startwork":
        print("Start Work", action)
        startwork()
    elif action == "stopwork":
        print("Stop Work", action)
        stopwork()
    

    print("************************************************")