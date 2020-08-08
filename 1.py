import tkinter as tk
import pyautogui
import pydirectinput
import pywinauto
import time
import recorder
import os
import json
import threading
import multiprocessing
import datetime
import math
import cv2 as cv
import numpy as np
from pynput import mouse

class btnType():
    MENU = "menu"
    PETS = 'pets'
    DELETE = 'delete'
    YES = 'yes'
    CONFIRM = 'confirm'

#Constants
COUNTDOWN_TIME = 3
TIME_BETWEEN_COMMANDS = 1
REPORT_TIME = 10
SLEEP_TIME = 900
BUTTONS = {
    btnType.MENU : {"x" : 2360, "y" : 661,"r":86,"g":181,"b":255}, 
    btnType.PETS : {"x" : 849, "y" : 471,"r":255,"g":145,"b":86},
    btnType.DELETE: {"x" : 1395, "y" : 385,"r":255,"g":181,"b":109},
    btnType.YES : {"x" : 1077, "y" : 746,"r":0,"g":223,"b":160},
    btnType.CONFIRM : {"x" : 1047, "y" : 1056,"r":0,"g":223,"b":160}
}
LOCATION_FILENAME = 'btn_positions'
BUTTON_WIDTH = 40
BUTTON_HEIGHT = 2
CHECK_W = 7
CHECK_H = 7
CHECK_CONFIDENCE = 0.95

#Global Variables
window = None
myLabel = None
errorLabel = None
lblSetMenu = None
lblSetPets = None
lblSetDelete = None
lblSetYes = None
lblSetConfirm = None
btnStart = None
btnStop = None
thread = None
stop_thread = None
btnSetMenu = None
btnSetPets = None
btnSetDelete = None
btnSetYes = None
btnSetConfirm = None
btnStart = None
btnStop = None
btnTimePlus = None
btnTimeMinus = None
lblWaitTime = None
btnSpeedPlus = None
btnSpeedMinus = None
lblSpeed = None
mouse_listener = None
isPressed = False

#TODO: 
#   - Kill Timer thread when stop button is pushed (IMPORTANT)
#   - Pause rolling while deleting pets
#   - Speed up click intervals and increase reliability by checking if mouse click was successful
#   - Check for open pets menu and skip menu and pets button clicks
#   - Find a way to make object detection work if window is moved or resized
#   - Text detection to find money per second, total money, and amount needed to rebirth
#   - Rebirth automatically when money == rebirth amount
# 
# STRETCH GOALS
#   - Identify all pets in inventory and auto equip selected pets
#   - Auto shiny and starry selected pets
#   - Auto play minigames

### MAIN ###

def main():
    init_listener()
    init_tk()
    init_locations()
    global window
    window.mainloop()

### FUNCTIONS ###

#initialize gui window
def init_tk():
    global window
    global myLabel
    window = tk.Tk()
    window.title('Pet Ranch Bot')
    global errorLabel
    global lblSetConfirm
    global lblSetDelete
    global lblSetMenu
    global lblSetPets
    global lblSetYes    
    global btnSetMenu
    global btnSetPets
    global btnSetDelete
    global btnSetYes
    global btnSetConfirm
    global btnStart
    global btnStop
    global lblSpeed
    global lblWaitTime
    global SLEEP_TIME
    global TIME_BETWEEN_COMMANDS
    myLabel = tk.Label(window, text="Pet Ranch Clicker", font=('Lucida Sans Typewriter', 32, 'bold'), height=2)
    btnSetMenu = tk.Button(window, text='Set Main Menu Position', width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=btnSetMenu_click)
    btnSetPets = tk.Button(window, text='Set Pets Button Position', width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=btnSetPets_click)
    btnSetDelete = tk.Button(window, text='Set Delete Button Position', width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=btnSetDelete_click)
    btnSetYes = tk.Button(window, text='Set Yes Button Position', width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=btnSetYes_click)
    btnSetConfirm = tk.Button(window, text='Set Confirm Button Position', width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=btnSetConfirm_click)
    btnStart = tk.Button(window, text="Start", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=start_click)
    btnStop = tk.Button(window, text='Stop', width=BUTTON_WIDTH, height=BUTTON_HEIGHT, command=stop, state='disabled')
    btnTimeMinus = tk.Button(window, text='-', width=math.floor(BUTTON_WIDTH/2)-1, height=math.floor(BUTTON_HEIGHT), command=btnTimeMinus_Click)
    btnTimeMinus.bind("<Button-1>", btnTimeMinus_Click)
    btnTimePlus = tk.Button(window, text='+', width=math.floor(BUTTON_WIDTH/2)-1, height=math.floor(BUTTON_HEIGHT), command=btnTimePlus_Click)
    btnTimePlus.bind("<Button-1>", btnTimePlus_Click)
    btnSpeedMinus = tk.Button(window, text='-', width=math.floor(BUTTON_WIDTH/2)-1, height=math.floor(BUTTON_HEIGHT), command=btnSpeedMinus_Click)
    btnSpeedPlus = tk.Button(window, text='+', width=math.floor(BUTTON_WIDTH/2)-1, height=math.floor(BUTTON_HEIGHT), command=btnSpeedPlus_Click)
    lblSetMenu = tk.Label(window, text="")
    lblSetPets = tk.Label(window, text="")
    lblSetDelete = tk.Label(window, text="")
    lblSetYes = tk.Label(window, text="")
    lblSetConfirm = tk.Label(window, text="")
    lblWaitTime = tk.Label(window, text="Wait Time: {:02d}:{:02d}".format(math.floor(SLEEP_TIME/60) , SLEEP_TIME%60), font=('Calibri', 16, 'bold'))
    lblSpeed = tk.Label(window, text="Time between clicks: {}s".format(TIME_BETWEEN_COMMANDS), font=('Calibri', 16, 'bold'))
    myLabel.grid(row=0, column=0, columnspan=4)
    btnSetMenu.grid(row=1, column=0, columnspan=2)
    btnSetPets.grid(row=2, column=0, columnspan=2)
    btnSetDelete.grid(row=3, column=0, columnspan=2)
    btnSetYes.grid(row=4, column=0, columnspan=2)
    btnSetConfirm.grid(row=5, column=0, columnspan=2)
    btnTimeMinus.grid(row=6,column=0)
    btnTimePlus.grid(row=6,column=1)
    btnSpeedMinus.grid(row=7,column=0)
    btnSpeedPlus.grid(row=7,column=1)
    btnStart.grid(row=10,column=0, columnspan=2)
    btnStop.grid(row=10, column=2, columnspan=2)
    lblSetMenu.grid(row=1, column=2, columnspan=2)
    lblSetPets.grid(row=2, column=2, columnspan=2)
    lblSetDelete.grid(row=3, column=2, columnspan=2)
    lblSetYes.grid(row=4, column=2, columnspan=2)
    lblSetConfirm.grid(row=5, column=2, columnspan=2)
    lblWaitTime.grid(row=6, column=2, columnspan=2)
    lblSpeed.grid(row=7, column=2, columnspan=2)

# load click locations from json file and set label text to x and y coordinates
def init_locations():
    print('INITLOCATIONS')
    global BUTTONS
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join(
        script_dir, 
        'Recordings', 
        '{}.json'.format(LOCATION_FILENAME)
    )

    try:
        with open(filepath, 'r') as jsonFile:
            data = json.load(jsonFile)
            for item in data:
                try:
                    BUTTONS[item['btn']]["x"],BUTTONS[item['btn']]["y"] = item['info']['pos'].values()
                except KeyError:
                    print("Button not found")
        jsonFile.close()
    except FileNotFoundError:
        with open(filepath, 'w') as create:
            create.close()
    global lblSetMenu
    print(lblSetMenu)
    lblSetMenu.config(text="{}, {}".format(BUTTONS[btnType.MENU]["x"],BUTTONS[btnType.MENU]["y"]))
    global lblSetPets
    print(lblSetPets)
    lblSetPets.config(text="{}, {}".format(BUTTONS[btnType.PETS]["x"],BUTTONS[btnType.PETS]["y"]))
    global lblSetDelete
    print(lblSetDelete)
    lblSetDelete.config(text="{}, {}".format(BUTTONS[btnType.DELETE]["x"],BUTTONS[btnType.DELETE]["y"]))
    global lblSetYes
    print(lblSetYes)
    lblSetYes.config(text="{}, {}".format(BUTTONS[btnType.YES]["x"],BUTTONS[btnType.YES]["y"]))
    global lblSetConfirm
    print(lblSetConfirm)
    lblSetConfirm.config(text="{}, {}".format(BUTTONS[btnType.CONFIRM]["x"],BUTTONS[btnType.CONFIRM]["y"]))
    
    return False        

# Activate the Roblox window
def init_window():
    try:
        app = pywinauto.Application().connect(title_re='Roblox')
        app.Roblox.set_focus()
        return True
    except pywinauto.findwindows.ElementNotFoundError:
        print('Window not found')

def init_listener():
    print("INITLISTENER")
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
       

# Open roblox window and start mouse listener
def btn_callback(type):
    global mouse_listener
    mouse_listener.stop()
    global window
    window.wm_state('iconic')
    if init_window():
        disable_buttons(type)
        r = recorder.recorder()
        r.runListeners(type)
        r.write()
        del r
        init_locations()
        enable_buttons()
    else:
        print("Can't find the window")    
    #   global errorLabel
    #   errorLabel.config(text="Couldn't find window 'Roblox'")
    mouse_listener.start()
    window.focus_force()
    window.wm_state('normal')

def btnSetMenu_click():
    btn_callback(btnType.MENU)

def btnSetPets_click():
    btn_callback(btnType.PETS)

def btnSetDelete_click():
    btn_callback(btnType.DELETE)

def btnSetYes_click():
    btn_callback(btnType.YES)

def btnSetConfirm_click():
    btn_callback(btnType.CONFIRM)

def update_window():
    global window
    window.update()

# Function to handle key presses
def press(button, seconds=1):
    pydirectinput.keyDown(button)
    print("Pressed " + button)
    time.sleep(seconds)
    pydirectinput.keyUp(button)
    
    print("Released " + button)
    time.sleep(TIME_BETWEEN_COMMANDS)

def click(x,y,speed=.5,seconds=1):
    time.sleep(speed)
    pydirectinput.moveTo(x,y,0.01)
    time.sleep(0.01)
    pydirectinput.moveTo(x-5,y-5,0.01)
    time.sleep(0.01)
    pydirectinput.moveTo(x+5,y+5,0.01)
    time.sleep(0.01)
    pydirectinput.moveTo(x-5,y+5,0.01)
    time.sleep(0.01)
    pydirectinput.click(x=x,y=y,duration=seconds)
    print('Clicked ',(x,y))

def myLabel_message(message):
    global myLabel
    global stop_thread
    stop_thread = False
    counter = 0
    dots = "..."
    while not stop_thread:
        subdots = dots[0:counter%3+1]
        print(subdots)
        myLabel.config(text="{}{}".format(message,subdots))
        update_window()
        counter += 1
        time.sleep(1)


def report_position():
    for i in range(0, REPORT_TIME):
        print(pyautogui.position())
        time.sleep(1)
    time.sleep(TIME_BETWEEN_COMMANDS)

def start_click():
    global thread
    global btnStop
    btnStop.config(state='normal')
    update_window()
    global stop_thread
    stop_thread = False
    thread = threading.Thread(target=loop)
    thread.start()

def loop():
    global myLabel
    global stop_thread
    global SLEEP_TIME
    disable_buttons('None')
    while init_window() and (not stop_thread):

        try:
            global thread
            wake_up()
            time.sleep(1)
            delete_pets()
            time.sleep(1)
            start_rolling()
            time.sleep(1)
            stop_thread = False
            for i in range(0,math.floor(SLEEP_TIME)):
                if stop_thread:
                    return
                startTime = time.time()
                blink = ": "[i%2:(i%2)+1]
                myLabel.config(text="Waiting{} {:02d}:{:02d}".format(blink, math.floor(i/60) , i%60))
                update_window()
                executionTime = time.time()-startTime
                if executionTime < 1:
                    time.sleep(1-executionTime)
                print(i)
        except RuntimeError:
            time.sleep(300)
            continue

def stop():
    global stop_thread
    stop_thread = True
    global thread
    thread = None
    global btnStop
    btnStop.config(state='disabled')
    enable_buttons()


def disable_buttons(active_button):
    global btnSetMenu
    global btnSetPets
    global btnSetDelete
    global btnSetYes
    global btnSetConfirm
    global btnStart

    btnSetMenu.config(state='disabled')
    btnSetPets.config(state='disabled')
    btnSetDelete.config(state='disabled')
    btnSetYes.config(state='disabled')
    btnSetConfirm.config(state='disabled')
    btnStart.config(state='disabled')

def enable_buttons():
    global btnSetMenu
    global btnSetPets
    global btnSetDelete
    global btnSetYes
    global btnSetConfirm
    global btnStart

    btnSetMenu.config(state='normal')
    btnSetPets.config(state='normal')
    btnSetDelete.config(state='normal')
    btnSetYes.config(state='normal')
    btnSetConfirm.config(state='normal')
    btnStart.config(state='normal')

def pause_between_commands(multiplier=1):
    global TIME_BETWEEN_COMMANDS
    time.sleep(TIME_BETWEEN_COMMANDS*multiplier)

def btnTimePlus_Click(event):
    global SLEEP_TIME
    global lblWaitTime
    global isPressed
    d  = 1
    while isPressed:
        if SLEEP_TIME > 0:
            SLEEP_TIME+=d
            d += 0.2
            lblWaitTime.config(text="Wait Time: {:02d}:{:02d}".format(math.floor(SLEEP_TIME/60), math.floor(SLEEP_TIME%60)))
            update_window()
            time.sleep(0.1)

def btnTimeMinus_Click(event):
    global SLEEP_TIME
    global lblWaitTime
    global isPressed
    print("ISPRESSED: {}".format(isPressed))
    d = 1
    while isPressed:
        if SLEEP_TIME > 1:
            SLEEP_TIME-=d
            d+=0.2
            lblWaitTime.config(text="Wait Time: {:02d}:{:02d}".format(math.floor(SLEEP_TIME/60), math.floor(SLEEP_TIME%60)))
            update_window()
            time.sleep(0.1)

def btnSpeedPlus_Click():
    global TIME_BETWEEN_COMMANDS
    global lblSpeed
    if TIME_BETWEEN_COMMANDS >= 0.1:
        TIME_BETWEEN_COMMANDS += 0.1
        lblSpeed.config(text="Time between clicks: {:02.02f}s".format(TIME_BETWEEN_COMMANDS))
        update_window()

def btnSpeedMinus_Click():
    global TIME_BETWEEN_COMMANDS
    global lblSpeed
    if TIME_BETWEEN_COMMANDS > 0.1:
        TIME_BETWEEN_COMMAND -= 0.1
        lblSpeed.config(text="Time between clicks: {:02.02f}s".format(TIME_BETWEEN_COMMANDS))
        update_window()

def isColourInArea(r, g, b, x, y):

    pic = pyautogui.screenshot(region=(x-30, y-30, 30, 30))

    #convert screenshot to numpy array for opencv to use
    #cvImg = cv.cvtColor(np.array(pic), cv.COLOR_RGB2BGR)

    #cv.imshow("Search Area", cvImg)
    #cv.waitKey(0)
    width, height = pic.size
    start_time = time.time()
    for w in range(0, width, 5):
        for h in range(0, height, 5):
            pr,pg,pb = pic.getpixel((w, h))
            #print("{} at {},{}. Colour = ({}, {}, {})".format(pixel,(x+1)-w,(y+1)-h,r,g,b))
            if(isCloseEnough(pr, r) and isCloseEnough(pg, g) and isCloseEnough(pb, b)):
                print("FOUND AFTER {} TRIES - elapsed: {}".format((w+1)*(h+1), time.time()-start_time))
                return True

    
    print("NOT FOUND - elapsed: {}".format(time.time()-start_time))
    return False
    
def isCloseEnough(num1, num2):
    num2_lower = math.floor(num2*CHECK_CONFIDENCE)
    h_percent = 1+(1-CHECK_CONFIDENCE)
    num2_higher = math.ceil(num2*h_percent)
    if num2_lower <= num1 <= num2_higher:
        return True
    else:
        return False

def on_click(x,y,button,pressed):
    global isPressed
    if pressed:
        print("Pressed")
        isPressed = True
    else:
        print("Released")
        isPressed = False

### ACTION FUNCTIONS ###
def starting():
    print("Starting", end='')
    for i in range(0,COUNTDOWN_TIME):
        print(".", end='')
        time.sleep(1)
    print("")
    pause_between_commands()

def wake_up():
    press('space', .3)
    pause_between_commands()

def stop_rolling():
    pass



def delete_pets():

    """
        NEW TEST
        CHECK IF BUTTON EXISTS IN AREA <--
        IF YES:                          |
            CLICK                        |
        ELSE:                            |
            CHECK THE NEXT BUTTON---------
    """
    for index, button in enumerate(BUTTONS.values()):
        r = button["r"]
        g = button["g"]
        b = button["b"]
        x = button["x"]
        y = button["y"]
        if button == BUTTONS[btnType.MENU]:
            attempt = 0
            while(isColourInArea(255,145,86,BUTTONS[btnType.PETS]['x'],BUTTONS[btnType.PETS]['y']) == False):
                print("PETS = FALSE")
                click(x,y,0.1,0.3)
                time.sleep(0.01)
                attempt += 1
                if attempt > 6:
                    print("LEAVING AT PETS BUTTON")
                    break
            continue
        attempt = 0
        showing = True
        while(showing):
            click(x,y,0.3,0.01)
            time.sleep(0.1)
            attempt += 1
            if attempt > 6:
                break
            showing = isColourInArea(r,g,b,x,y)
    
    """
    attempt = 0
    while(isColourInArea(255,181,109,BUTTONS[btnType.DELETE]['x'],BUTTONS[btnType.DELETE]['y']) == False):
        print("PETS = FALSE")
        click(BUTTONS[btnType.PETS]['x'],BUTTONS[btnType.PETS]['y'],0.31,0.3)
        time.sleep(0.01)
        attempt += 1
        if attempt > 6:
            print("LEAVING AT PETS BUTTON")
            pause_between_commands()
            return

    attempt = 0
    while(isColourInArea(0,223,160,BUTTONS[btnType.YES]['x'],BUTTONS[btnType.YES]['y']) == False):
        print("DELETE = FALSE")
        click(BUTTONS[btnType.DELETE]['x'],BUTTONS[btnType.DELETE]['y'],0.3,0.3)
        time.sleep(0.01)
        attempt += 1
        if attempt > 3:
            print("LEAVING AT PETS BUTTON")
            pause_between_commands()
            return

    attempt = 0
    while(isColourInArea(0,223,160,BUTTONS[btnType.CONFIRM]['x'],BUTTONS[btnType.CONFIRM]['y']) == False):
        print("YES = FALSE")
        click(BUTTONS[btnType.YES]['x'],BUTTONS[btnType.YES]['y'],0.3,0.3)
        time.sleep(0.01)
        attempt += 1
        if attempt > 3:
            print("LEAVING AT PETS BUTTON")
            pause_between_commands()
            return

    while(isColourInArea(0,223,160,BUTTONS[btnType.CONFIRM]['x'],BUTTONS[btnType.CONFIRM]['y'])):
        click(BUTTONS[btnType.CONFIRM]['x'],BUTTONS[btnType.CONFIRM]['y'],1,0.3)
        time.sleep(0.01)
    """
    pause_between_commands()


def start_rolling():
    press('t',.3)

if __name__ == "__main__":
    main()
