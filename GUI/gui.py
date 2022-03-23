
import cv2
import numpy as np
import os
import sys
import requests
from PIL import Image
#import face_recognition
import io
import PySimpleGUI as sg


def homeLayout():
    left_col = [
        [sg.Text("DRAWBUDDY")],
        [sg.Button('Host')],
        [sg.Button('Attendee')]
    ]

##    right_col = [
##        [sg.Text("Webcam Playback (Press Space to Begin Login/Signup)")],
##        [sg.Text(size=(40, 1), key="-TOUT_GREET-")],
##        [sg.Image(key="-IMAGE_GREET-")],
##    ]

    layout = [[sg.Column(left_col)]]

    return layout

def hostLayout():
    left_col = [
        [sg.Text('Please Enter Your Name')],
        [sg.Input(key = '-NEWNAME-')],
        [sg.Button('Submit')],
        [sg.Button('Lock Face')],
        [sg.Button('Exit1')]
    ]

    right_col = [
        [sg.Text("Webcam Playback (Press Space to Begin Login/Signup)")],
        [sg.Text(size=(40, 1), key="-TOUT-SIGNUP-")],
        [sg.Image(key="-IMAGE_SIGNUP-")]
    ]

    layout = [[sg.Column(left_col), sg.Column(right_col)]]

    return layout

def attendeeLayout():
    return [[]]

def whiteboardLayout():
    return [[]]

LAYOUTS = [[sg.Column(homeLayout(), key = '-HOME-')],
            [sg.Column(hostLayout(), key = '-HOST-', visible = False)],
            [sg.Column(attendeeLayout(), key = '-ATTENDEE-', visible = False)],
            [sg.Column(whiteboardLayout(), key = '-WHITEBOARD-', visible = False)]
           ]


# takes frame and returns bytes of frame compatible with cv
def get_bytes(frame):
    return cv2.imencode('.png', frame)[1].tobytes()

def cv2pil(cv):
        colorconv_cv = cv2.cvtColor(cv, cv2.COLOR_BGR2RGB)
        return Image.fromarray(colorconv_cv)

def pil2cv(pil):
    cv2im = np.array(pil)
    return cv2im[:,:,::-1] # reversing the z-axis (color channels: RGB -> BGR)

def resize_image(frame):
    framePIL = cv2pil(frame)
    framePIL = framePIL.resize((600,400))
    return pil2cv(framePIL)


def mainlooprun():
    window = sg.Window('Drawbuddy', LAYOUTS, background_color='#57B5EE',
                       resizable=True, finalize=True)
    window.set_min_size((500,500))

    cap = cv2.VideoCapture(0)
    #faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    iterations = 0
    while True:
        event, vals = window.read()
        print("event:", event, iterations)
        ret, frame = cap.read()

        #if event == 'New User':
 
        #if event == 'Lock Face':

        #if event == 'Submit':
            

        if event == 'Host': # Returning User
             window['-HOME-'].update(visible = False)
             window['-HOST-'].update(visible = True)

        if event == sg.WIN_CLOSED or event == 'Exit1':
            break

        window.refresh()

        iterations += 1
    window.close()

mainlooprun()
