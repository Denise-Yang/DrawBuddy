#Parses SVG file and extracts lines to covnert to graph objects
import cv2
import numpy as np
import math
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
import string
from queue import Queue
from svgutils.compose import *
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import io
#from svgpathtools import svg2paths

def getTheta(points, i, prevIdx):
    x0 = points[prevIdx][0]
    y0 = points[prevIdx][1]
    x1 = points[i][0]
    y1 = points[i][1]
    x2 = points[i+1][0]
    y2 = points[i+1][1]

    mag0 = math.sqrt(pow(y0-y1, 2) + pow(x0-x1, 2))
    mag1 = math.sqrt(pow(y2-y1, 2) + pow(x2-x1, 2))

    dot = (x0-x1)*(x2-x1) + (y0-y1)*(y2-y1)
    if (dot/(mag0*mag1)>1 or dot/(mag0*mag1)<-1 ):
        return math.pi

    return math.acos(dot/(mag0*mag1))

def getData(fileName):            
    paths = []
    with open(fileName) as svgFile:
        for svgStr in svgFile:
            pointsI = []
            points = []
            if "path" in svgStr:
                index = svgStr.find("C")
                end = svgStr.find("Z")

                startPath = svgStr[index:end]
                #print(startPath)

                coordinates = startPath.split("C")
                for coord in coordinates:
                    point = coord.split(" ")

                    if len(point) > 1:
                        x = point[4]
                        y = point[5]
                        pointsI.append((float(x),float(y)))
                        #print(  x + ",", y)

     
                #just do enpoints, could add additional chekcs to determine circle or non circle
                points.append(pointsI[0])
                points.append[pointsI[len(pointsI)-1]]

                
                #filter points
                """points.append(pointsI[0])
                prevIdx = 0
                for i in range(1,len(pointsI)-1):
                    theta = getTheta(pointsI,i,prevIdx)
                    if theta < 11*math.pi/20:
                        points.append(pointsI[i])
                        prevIdx = i
                points.append(pointsI[len(pointsI)-1])
                paths.append(points)
                """

                """for i in range(len(points)):  
                    x1 = points[i][0]
                    y1 = points[i][1]
                    print("(", str(x1)+", "+ str(y1)+")", end =" ")   
                print()
                """

    return paths




           # x1, y1, x2, y2 = getPointsFromLine(svgStr)