import cv2
import numpy as np
import os
import sys
import requests
from PIL import Image as IMG
import io
import PySimpleGUI as sg
import random
import pyautogui as ag
import subprocess
import time
import base64
import socket
import threading
from queue import Queue
from svgutils.compose import *
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import io
from svgParser import getData


isHost = False
myID = ""
userList = dict()
PORT = random.randint(3456, 59897)
def start_serv():
    os.system("python3 Server.py " + str(PORT))

HOST = "172.26.93.96" # put your IP address here if playing on multiple computers

def handleServerMsg(server, serverMsg):
    server.setblocking(1)
    msg = ""
    command = ""
    while True:
        msg += server.recv(10).decode("UTF-8")
        command = msg.split("\n")
        while (len(command) > 1):
            readyMsg = command[0]
            msg = "\n".join(command[1:])
            serverMsg.put(readyMsg)
            command = msg.split("\n")

def mkGreetLayout():
    height, width = ag.size()
    button_font = ('Courier', 60)
    center_col = [ 
        [sg.Text("DrawBuddy", font=("Courier", 100))],
        [sg.Button('Create Session', size=(15,1), font=button_font)],
        [sg.Button('Join Session', size=(15,1), font=button_font)]
    ]
    layout = [[sg.Column(center_col)]]

    return layout 

def mkHostLayout():
    code = PORT
    if len(str(code)) == 4:
        code = "0" + str(code)
    left_col = [
        [sg.Text("Here is Your Access Code", font=('Courier', 50))],
        [sg.Text(code, font=('Courier', 40))],
        [sg.Text("Enter Your Display Name:", font=('Courier', 40)), sg.InputText(key='-DISNAME0-', font=('Courier', 40))],
        [sg.Button('Back', font=('Courier', 40)), sg.Button('Start', font=('Courier', 40))]
    ]
    
    layout = [[sg.Column(left_col)]]

    return layout
    
def get_names(users):
    res = ''
    for key in users:
        res += str(users[key]) + '\n'
    return res[:-1] 
    
def mkUserLayout():
    left_col = [
        [sg.Text("Enter the Access Code", font=('Courier', 50))],
        [sg.InputText(key='-PORTNUM-', font=('Courier', 40))],
        [sg.Text("Enter Your Display Name:", font=('Courier', 40)), sg.InputText(key='-DISNAME1-', font=('Courier', 40))],
        [sg.Button("Join", font=('Courier', 40)), sg.Button('Back', font=('Courier', 40))]
    ]
    layout = [[sg.Column(left_col)]]

    return layout
    
def whiteboardLayout():
    global userList

    code = "0" + str(PORT) if len(str(PORT)) == 4 else str(PORT)

    left_col = [[sg.Text("Whiteboard ")],
                [sg.Text(get_names(userList), key='-USERLIST-')],
                [sg.Image(key="-IMAGE-")],
                [sg.Graph(
                canvas_size=(550, 675),
                graph_bottom_left=(0, 0),
                graph_top_right=(550, 675),
                key="-GRAPH-",
                change_submits=True,  # mouse click events
                background_color='lightblue',
                drag_submits=True)]
    ]
    
    camera_col = [[sg.Text("Camera Feed")],        
        [sg.Text(code, key='-PORT-')],
        [sg.Button('Receive')],
        [sg.Button('Send')],
        [sg.Button('Vectorize Image')],
        [sg.Image(key="-IMAGE_FEED-")],
        [sg.Image(key="-VECTORIZE_IMAGE-")]]
    
    layout = [[sg.Column(left_col, size = (550, 675), background_color = 'white'),
               sg.Column(camera_col, size = (400, 600), background_color = 'white')]]
    
    return layout

sz=(900,700)
LAYOUTS = [[sg.Column(mkGreetLayout(), key = '-GREET-', visible = False),
            sg.Column(mkHostLayout(), key = '-HOST-', visible = False),
            sg.Column(mkUserLayout(), key = '-USER-', visible = False),
            sg.Column(whiteboardLayout(), key = '-WHITEBOARD-', visible = True, background_color = 'white')]]

# takes frame and returns bytes of frame compatible with cv
def get_bytes(frame):
    return cv2.imencode('.png', frame)[1].tobytes()

def convertToImage(frame):
    return cv2.imencode('.png', frame)

def saveImage(frame, file_name):
    current_dir = os.getcwd()
    path = current_dir[:-3] + "vectorization/images"
    cv2.imwrite(os.path.join(path , file_name+'.jpg'), frame)
    return file_name+'.jpg'
   
def cv2pil(cv):
    colorconv_cv = cv2.cvtColor(cv, cv2.COLOR_BGR2RGB)
    return IMG.fromarray(colorconv_cv)

def pil2cv(pil):
    cv2im = np.array(pil)
    return cv2im[:,:,::-1] # reversing the z-axis (color channels: RGB -> BGR)

def resize_image_signup(frame):
    framePIL = cv2pil(frame)
    framePIL = framePIL.resize((200,150))
    return pil2cv(framePIL)

def resize_image_home_page(frame):
    framePIL = cv2pil(frame)
    framePIL = framePIL.resize((300,200))
    return pil2cv(framePIL)

def vectorize(frame, file_name):
    path =  os.getcwd()
    base_path =path[:-3] + "vectorization/images"
    base_path1 =path[:-3] + "vectorization/results"
    input_path = os.path.join(base_path , file_name +'.jpg')
    output_path = os.path.join(base_path1 , file_name+'.svg')
    cv2.imwrite(input_path, frame)
    convert = subprocess.run("vtracer --input " + input_path + " --output " + output_path, shell =True)

def mainlooprun():
    global PORT
    global HOST
    global myID
    global userList
    global isHost
    window = sg.Window('Login App',LAYOUTS, size=sz, background_color='#57B5EE',
                       resizable=True, finalize=True)
    window.set_min_size(sz)
    cap = cv2.VideoCapture(0)
    iterations = 0
    vectorize_image = False
    image_to_vectorize = None
    
    while True:
        event, vals = window.read(timeout=10)
        try:
            while(serverMsg.qsize() > 0):
                msg = serverMsg.get(False)
                print("received: ", msg, "\n")
                msg = msg.split("\t")
                command = msg[0]
                if command == 'myIDis':
                    myID = msg[1]
                    i = 2
                    try:
                        while True:
                            userList[msg[i]] = msg[i+1]
                            i += 2
                    except:
                        userList[myID] = vals['-DISNAME0-'] if myID == 'user1' else vals['-DISNAME1-']
                if command == 'newUser':
                    userList[msg[1]] = 'newUser'
                if command == 'dname':
                    userList[msg[1]] = msg[2]
        except:
            pass

        if event != "__TIMEOUT__":
            print("event:", event)

        code = vals['-PORTNUM-'] if not isHost else "0" + str(PORT) if len(str(PORT)) == 4 else str(PORT)
        ret, frame = cap.read()
        window['-IMAGE_FEED-'].update(data = get_bytes(resize_image_home_page(frame)))
        window['-USERLIST-'].update(get_names(userList))
        window['-PORT-'].update(code)

        if vectorize_image:
            window['-VECTORIZE_IMAGE-'].update(data = get_bytes(resize_image_signup(image_to_vectorize)))
            vectorize_image = False

        if event == 'Create Session':
            window['-GREET-'].update(visible = False)
            window['-HOST-'].update(visible = True)
            
        if event == 'Join Session':
            window['-GREET-'].update(visible = False)
            window['-USER-'].update(visible = True)
            
        if event == 'Join':
            window['-USER-'].update(visible = False)
            PORT = int(vals['-PORTNUM-'])
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((HOST,PORT))
            serverMsg = Queue(100)
            threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
            msg = 'dname\t' + vals['-DISNAME1-'] + '\n'
            server.send(msg.encode())
            window['-WHITEBOARD-'].update(visible = True)

        if event == 'Start':
            threading.Thread(target=start_serv).start()
            time.sleep(5)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((HOST, PORT))
            serverMsg = Queue(100)
            threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
            msg = 'dname\t' + vals['-DISNAME0-'] + '\n'
            server.send(msg.encode())
            isHost = True
            window['-HOST-'].update(visible = False)
            window['-WHITEBOARD-'].update(visible = True)

        if event == "Vectorize Image":
            vectorize_image = True
            image_to_vectorize = frame
            file_name =  'frame'
            vectorize(frame, file_name)
            base_path1 = os.getcwd()[:-3] + "vectorization/results"
            output_path = os.path.join(base_path1 , file_name+'.svg')
            drawing = svg2rlg(output_path)
            renderPM.drawToFile(drawing, file_name + ".png", fmt="PNG")
            image = IMG.open(file_name + ".png")
            getData(output_path)
            image.thumbnail((500, 500))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            window['-IMAGE-'].update(data=bio.getvalue())
            
        if event == 'Back' or event == 'Back0':
            window['-USER-'].update(visible = False)
            window['-HOST-'].update(visible = False)
            window['-GREET-'].update(visible = True)
            
        if event == sg.WIN_CLOSED or event == 'Exit1':
            break

        window.refresh()

        iterations += 1
    cap.release()
    window.close()


mainlooprun()
