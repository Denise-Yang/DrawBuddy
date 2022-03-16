
import cv2
import numpy as np
import os
import sys
import requests
from PIL import Image
#import face_recognition
import io
import PySimpleGUI as sg


def mkGreetLayout():
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

def mkSignupLayout():
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

def mkLoginLayout():
    return [[]]

LAYOUTS = [[sg.Column(mkGreetLayout(), key = '-GREET-')],
            [sg.Column(mkSignupLayout(), key = '-SIGNUP-', visible = False)],
            [sg.Column(mkLoginLayout(), key = '-LOGIN-', visible = False)]]

#### BEGIN: code from previous file #### 

def get_diff(i1, i2): 

    face_embeddings_i2 = np.array(face_recognition.face_encodings(i2))
    face_embeddings_i1 = np.array(face_recognition.face_encodings(i1))

    return sum(sum(abs(face_embeddings_i2 - face_embeddings_i1)))


def compute_diff_scores(i1, i2): # params: full frame (a_face), crop(a_face_only)
    scores = []
    filenames = []

    users = os.listdir('./saved_faces')

    k = 0
    while (k < len(users)):
        file = users[k]
        if (file.endswith('.png')):
            if (file.endswith('_pp.png')):
                name = file[:file.index('_pp.png')]
                if mode == 'debug': print('comparing with ' + name)
                filenames.append(name)
                i3 = cv2.imread('./saved_faces/'+name+'_pp.png')
                diff = get_diff(i3, i2)
                scores.append(diff)
        k = k + 1

    return scores, filenames

#### END: code from previous file #### 

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
    window = sg.Window('Login App',LAYOUTS)
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
            

        if event == 'Returning User': # Returning User
             window['-GREET-'].update(visible = False)
             window['-LOGIN-'].update(visible = True)

        if event == sg.WIN_CLOSED or event == 'Exit1':
            break

        window.refresh()

        iterations += 1
    window.close()

mainlooprun()
