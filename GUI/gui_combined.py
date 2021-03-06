
import cv2
import numpy as np
import os
import sys
import requests
from PIL import Image
import io
import PySimpleGUI as sg
import random
import pyautogui as ag


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
    code = random.randint(3456, 59897)
    if len(str(code)) == 4:
        code = "0" + str(code)
    left_col = [
        [sg.Text("Here is Your Access Code")],
        [sg.Text(code), sg.Button('Start')],
        [sg.Text("Joined Users")],
        [sg.Text("NOT IMPLEMENTED")]
    ]
    
    layout = [[sg.Column(left_col)]]

    return layout
    
    
def mkUserLayout():
    left_col = [
        [sg.Text("Enter the Access Code")],
        [sg.InputText()],
        [sg.Button("Join")]
    ]
    layout = [[sg.Column(left_col)]]

    return layout
    
def whiteboardLayout():
    left_col = [[sg.Text("Whiteboard ")]]
    

    camera_col = [[sg.Text("Camera Feed")],
        [sg.Button('Receive')],
        [sg.Button('Send')],
        [sg.Button('Vectorize Image')],
        [sg.Image(key="-IMAGE_FEED-")]]
    
    layout = [[sg.Column(left_col, size = (550, 675), background_color = 'light blue'),
               sg.Column(camera_col, size = (400, 400), background_color = 'white')]
             ]
    
    return layout

sz=(900,700)
LAYOUTS = [[sg.Column(mkGreetLayout(), key = '-GREET-')],
            [sg.Column(mkHostLayout(), key = '-HOST-', visible = False)],
            [sg.Column(mkUserLayout(), key = '-USER-', visible = False)],
            [sg.Column(whiteboardLayout(), key = '-WHITEBOARD-', visible = False, background_color = 'white', size=sz)]]


# takes frame and returns bytes of frame compatible with cv
def get_bytes(frame):
    return cv2.imencode('.png', frame)[1].tobytes()

def cv2pil(cv):
        colorconv_cv = cv2.cvtColor(cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(colorconv_cv)

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


def mainlooprun():
    window = sg.Window('Login App',LAYOUTS, size=sz, background_color='#57B5EE',
                       resizable=True, finalize=True)
    window.set_min_size(sz)
    cap = cv2.VideoCapture(0)
    iterations = 0
    while True:
        event, vals = window.read(timeout=10)
        print("event:", event, iterations)
        ret, frame = cap.read()
        window.FindElement('-IMAGE_FEED-').Update(data = get_bytes(resize_image_home_page(frame)))
        
        if event == 'Create Session':
            window['-GREET-'].update(visible = False)
            window['-HOST-'].update(visible = True)
            
        if event == 'Join Session':
            window['-GREET-'].update(visible = False)
            window['-USER-'].update(visible = True)
            
        if event == 'Join' or event == 'Start':
            window['-HOST-'].update(visible = False)
            window['-USER-'].update(visible = False)
            window['-WHITEBOARD-'].update(visible = True)

        if event == sg.WIN_CLOSED or event == 'Exit1':
            break

        window.refresh()

        iterations += 1
    cap.release()
    window.close()


mainlooprun()
