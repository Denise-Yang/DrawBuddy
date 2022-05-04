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
from datetime import datetime as dt
import base64
import socket
import threading
from queue import Queue
from svgutils.compose import *
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import zlib
import io
from svgParser import parseSVG
from display import vectorizeImage
from display import groupLines

isHost = False
myID = ""
myUsername = ''
userList = dict()
vectors = 0
inbox = []
PORT = random.randint(3456, 59897)
def start_serv():
    os.system("python3 Server.py " + str(PORT))

HOST = "172.26.18.95" # put your IP address here if playing on multiple computers

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
        [sg.Button("Join", font=('Courier', 40)), sg.Button('Back', font=('Courier', 40))],
        [sg.Text("Sorry, Access Number Invalid Try Again", font=('Courierr', 40), key="-ERROR0-", visible=False)]
    ]
    layout = [[sg.Column(left_col)]]

    return layout
    
def whiteboardLayout():
    global userList

    code = "0" + str(PORT) if len(str(PORT)) == 4 else str(PORT)

    left_col = [[sg.Text("Whiteboard"), sg.Button('Exit')],
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
        [sg.Button('Receive', key='-REC-', visible=False), 
         sg.Text("Vectors in Inbox: %s" % str(vectors), text_color='white', 
                 background_color='red', key='-MREC-', visible=False)],
        [sg.Listbox(inbox, auto_size_text=True, select_mode='single',visible=False, key='-INBOX-'), sg.Button('Save', visible=False, key='-SAVE-')],
        [sg.InputText(key='-FILENAME-', visible=False), 
         sg.Button('Submit', key='-SUB-', visible=False), 
         sg.Button('Back', key='-USUB-', visible=False)],
        [sg.Button('Send', visible=False, key='-SBUTTON-')],
        [sg.Button('Vectorize Image')],
        [sg.Text('Could Not Vectorize Image Try Again', visible=False, key='-ERROR1-')],
        [sg.Image(key="-IMAGE_FEED-")],
        [sg.Image(key="-VECTORIZE_IMAGE-")],
        [sg.Button('Erase All', enable_events=True)],
        [sg.Checkbox('Delete Lines', key='-DELETELINES-', default=False)],
        [sg.Checkbox('Group Lines', key='-GROUPLINES-', default=False)]]
    
    layout = [[sg.Column(left_col, size = (550, 675), background_color = 'white'),
               sg.Column(camera_col, size = (400, 600), background_color = 'white')]]
    
    return layout

sz=(900,700)
LAYOUTS = [[sg.Column(mkGreetLayout(), key = '-GREET-', visible = True),
            sg.Column(mkHostLayout(), key = '-HOST-', visible = False),
            sg.Column(mkUserLayout(), key = '-USER-', visible = False),
            sg.Column(whiteboardLayout(), key = '-WHITEBOARD-', visible = False, background_color = 'white')]]

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

# def vectorize(frame, file_name):
#     path =  os.getcwd()
#     base_path =path[:-3] + "vectorization/images"
#     base_path1 =path[:-3] + "vectorization/results"
#     input_path = os.path.join(base_path , file_name +'.jpg')
#     output_path = os.path.join(base_path1 , file_name+'.svg')
#     cv2.imwrite(input_path, frame)    
#     cropImage(input_path)

#     convert = subprocess.run("vtracer --input " + input_path + " --output " + output_path, shell =True)

def mainlooprun():
    global PORT
    global HOST
    global myID
    global userList
    global isHost
    global vectors
    global myUsername
    global inbox
    receivedSVG = []
    window = sg.Window('Login App',LAYOUTS, size=sz, background_color='#57B5EE',
                       resizable=True, finalize=True)
    window.set_min_size(sz)
    cap = cv2.VideoCapture(0)
    iterations = 0
    image_to_vectorize = None

    dragging = False
    graph = window["-GRAPH-"]  # type: sg.Graph
    graph_size = (550, 675)
    start_point = end_point = None
    graphedLines = {}
    figureIndex = None
    graphedLines = {}
    
    while True:
        event, vals = window.read(timeout=10)
        if (vectors == 0):
            window['-MREC-'].update(visible=False)
        else:
            window['-MREC-'].update(visible=True)
        try:
            while(serverMsg.qsize() > 0):
                msg = serverMsg.get(False)
                msg = msg.split("\t")
                command = msg[0]
                print("received %s\n" % command)
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
                if command == 'send':
                    svg = msg[2].encode()
                    svg = base64.b64decode(msg[2])
                    svg = zlib.decompress(svg)
                    svg = svg.decode('UTF-8')
                    receivedSVG.append(svg)
                    vectors += 1
                    inbox.append('From: ' + userList[msg[1]] + ' at: ' + dt.now().strftime("%D-%H:%M:%S"))
                if command == 'exit':
                    userList.pop(msg[1])
        except:
            pass

        if event != "__TIMEOUT__":
            print("event:", event)
        try:
            code = vals['-PORTNUM-'] if not isHost else "0" + str(PORT) if len(str(PORT)) == 4 else str(PORT)
        except:
            pass
        ret, frame = cap.read()
        window['-IMAGE_FEED-'].update(data = get_bytes(resize_image_home_page(frame)))
        window['-USERLIST-'].update(get_names(userList))
        window['-PORT-'].update(code)
        window['-MREC-'].update("Vectors in Inbox: %s" % str(vectors))
        
        if (len(receivedSVG) == 0):
            window['-REC-'].update(visible=False)
        else:
            window['-REC-'].update(visible=True)

        if event == 'Create Session':
            window['-GREET-'].update(visible = False)
            window['-HOST-'].update(visible = True)
            
        if event == 'Join Session':
            window['-GREET-'].update(visible = False)
            window['-USER-'].update(visible = True)
            
        if event == 'Join':
            PORT = int(vals['-PORTNUM-'])
            try:
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.connect((HOST,PORT))
                serverMsg = Queue(100)
                threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()    
                myUsername = vals['-DISNAME1-']
                msg = 'dname\t' + vals['-DISNAME1-'] + '\n'
                server.send(msg.encode())
                window['-USER-'].update(visible = False)
                window['-WHITEBOARD-'].update(visible = True)
            except:
                window['-ERROR0-'].update(visible = True)

        if event == '-SBUTTON-':
            path = os.getcwd()[:-3] + "vectorization/results/frame.svg"
            f = open(path, 'r').read()
            compressed = f.encode()
            compressed = zlib.compress(compressed)
            compressed = base64.b64encode(compressed)
            compressed = str(compressed, 'utf-8')
            msg = 'send\t%s\n' % compressed
            server.send(msg.encode())

        if event == 'Start':
            threading.Thread(target=start_serv).start()
            time.sleep(2)
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect((HOST, PORT))
            serverMsg = Queue(100)
            threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
            myUsername = vals['-DISNAME0-']
            msg = 'dname\t' + vals['-DISNAME0-'] + '\n'
            server.send(msg.encode())
            isHost = True
            window['-HOST-'].update(visible = False)
            window['-WHITEBOARD-'].update(visible = True)

        if event == "Vectorize Image":
            try:
                window['-ERROR1-'].update(visible=False)
                graphedLines, figureIndex = vectorizeImage(frame, graph, graph_size, graphedLines, figureIndex)
                window['-SBUTTON-'].update(visible=True)            
            except Exception as e:
                print('error: ', e)
                window['-ERROR1-'].update(visible=True)

        if event == "-GRAPH-":
            x, y = vals["-GRAPH-"]
            if vals["-GROUPLINES-"] == True:
                graphedLines, figureIndex = groupLines(graph, x, y, graphedLines, figureIndex)
                drag_figures = graph.get_figures_at_location((x,y))
            if vals["-DELETELINES-"] == True:
                drag_figures = graph.get_figures_at_location((x,y))
                for fig in drag_figures:
                    (endpoint0, endpoint1) = graphedLines[fig]
                    x0 = endpoint0[0]
                    y0 = endpoint0[1]
                    x1 = endpoint1[0]
                    y1 = endpoint1[1]
                    graphedLines.pop(fig)
                    graph.delete_figure(fig)
            else:
                if not dragging:
                    start_point = (x, y)
                    dragging = True
                    drag_figures = graph.get_figures_at_location((x,y))
                    lastxy = x, y
                else:
                    end_point = (x, y)
                delta_x, delta_y = x - lastxy[0], y - lastxy[1]
                lastxy = x,y
                delete = []
                for fig in drag_figures:
                    (endpoint0, endpoint1) = graphedLines[fig]
                    x0 = endpoint0[0]
                    y0 = endpoint0[1]
                    x1 = endpoint1[0]
                    y1 = endpoint1[1]
                    newx0 = x0 + delta_x
                    newy0 = y0 + delta_y
                    newx1 = x1 + delta_x
                    newy1 = y1 + delta_y
                    x0diff = abs(x0 - x)
                    y0diff = abs(y0 - y)
                    x1diff = abs(x1 - x)
                    y1diff = abs(y1 - y)
                    rotating = False
                    if(x0diff < 15 and y0diff < 15): # rotating endpoint0
                        print("Rotating line: ", fig)
                        graph.draw_line((newx0 , newy0), (x1, y1), width=4)
                        rotating = True
                        delete.append(fig)
                        graphedLines[figureIndex] = [(newx0, newy0), (x1, y1)]
                        figureIndex += 1
                        graph.update()
                    elif(x1diff < 15 and y1diff < 15): # rotating endpoint1
                        print("Rotating line: ", fig)
                        graph.draw_line((x0 , y0), (newx1, newy1), width=4)
                        rotating = True
                        delete.append(fig)
                        graphedLines[figureIndex] = [(x0, y0), (newx1, newy1)]
                        figureIndex += 1
                        graph.update()
                    if not rotating:
                        graph.move_figure(fig, delta_x, delta_y)
                        graph.update()
                        print("moving figure ", fig)
                        graphedLines[fig] = [(newx0, newy0), (newx1, newy1)]
                    print("----------------------")
                for delFig in delete:
                    graph.delete_figure(delFig)
                    graphedLines.pop(delFig)
                # update drag_figures
                drag_figures = graph.get_figures_at_location((x,y))
                
        if event.endswith('+UP'):  # Drawing has ended because mouse up
            start_point, end_point = None, None
            dragging = False
            prior_rect = None

        if event == "Erase all":
            window['-GRAPH-'].erase()
            graphedLines = {}
            figureIndex = None
            
        if event == 'Back' or event == 'Back0':
            window['-USER-'].update(visible = False)
            window['-HOST-'].update(visible = False)
            window['-GREET-'].update(visible = True)

        if event == '-REC-':
            window['-REC-'].update(visible=False)
            window['-INBOX-'].update(visible=True)
            window['-SAVE-'].update(visible=True)
            window['-INBOX-'].update(inbox)
            
        if event == '-SAVE-':
            window['-INBOX-'].update(visible=False)
            window['-SAVE-'].update(visible=False)
            window['-FILENAME-'].update(visible=True)
            window['-SUB-'].update(visible=True)
            window['-USUB-'].update(visible=True)
            ind = inbox.index(vals['-INBOX-'][0])
            svg = receivedSVG.pop(ind)
            path = os.getcwd()[:-3]
            temp_name = str(time.time()).replace('.', '_')
            path += 'GUI/' + temp_name + '.svg'
            savedSVG = open(path, 'w')
            savedSVG.write(svg)
            drawing = svg2rlg(path)
            renderPM.drawToFile(drawing, temp_name + ".png", fmt="PNG")
            image = IMG.open(temp_name + ".png")
            image.thumbnail((500, 500))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            window['-VECTORIZE_IMAGE-'].update(data=bio.getvalue())
            os.remove(temp_name + '.png')
            os.remove(temp_name + '.svg')
            window['-VECTORIZE_IMAGE-'].update(visible=True)
            receivedSVG.insert(ind, svg)
        
        if event == '-SUB-':
            window['-REC-'].update(visible=True)
            window['-FILENAME-'].update(visible=False)
            window['-SUB-'].update(visible=False)
            window['-USUB-'].update(visible=False)
            window['-VECTORIZE_IMAGE-'].update(visible=False)
            fname = vals['-FILENAME-']
            ind = inbox.index(vals['-INBOX-'][0])
            svg = receivedSVG.pop(ind)
            path =  os.getcwd()[:-3]
            path += 'vectorization/results/' + fname + '.svg'
            savedSVG = open(path, 'w')
            savedSVG.write(svg)
            drawing = svg2rlg(path)
            renderPM.drawToFile(drawing, fname + ".png", fmt="PNG")
            image = IMG.open(fname + ".png")
            image.thumbnail((500, 500))
            bio = io.BytesIO()
            image.save(bio, format="PNG")
            window['-IMAGE-'].update(data=bio.getvalue())
            vectors-=1
            inbox.pop(ind)

        if event == '-USUB-':
            window['-REC-'].update(visible=True)
            window['-FILENAME-'].update(visible=False)
            window['-SUB-'].update(visible=False)
            window['-USUB-'].update(visible=False)
            vectors-=1
            ind = inbox.index(vals['-INBOX-'][0])
            inbox.pop(ind)
            receivedSVG.pop(ind)

        if event == sg.WIN_CLOSED or event == 'Exit':
            msg = 'exit\t%s\n' % myUsername
            server.send(msg.encode())
            time.sleep(1)
            window.close()
            break

        window.refresh()

        iterations += 1
    cap.release()
    window.close()


mainlooprun()
