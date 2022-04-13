#script for cropping image and extracting the white paper
#Denise Yang
#https://stackoverflow.com/questions/63001988/how-to-remove-background-of-images-in-python
#https://stackoverflow.com/questions/60794387/detect-white-rectangle-on-black-white-image-and-crop-opencv

import cv2 
import numpy as np

def show_image(image):
    cv2.imshow('image',image)
    c = cv2.waitKey()
    if c >= 0 : return -1
    return 0

def convertToBW(image_name):
    img = cv2.imread(image_name)
    contourIm = img.copy()
    grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 200, 255, cv2.THRESH_BINARY)
    #filter noise
    kernel = np.ones((10,10),np.uint8)
    result = cv2.morphologyEx(blackAndWhiteImage, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy  = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(contourIm, contours, -1, (0,255,0), 3)

    cv2.imshow("GRAY", contourIm)
    cv2.waitKey(0)

    print("done showing image")
    return contours

def removeBackground(image):
    contours, hierarchy  = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    result = image.copy()
    print(contours)

    cv2.drawContours(result, contours, -1, (0,255,0), 10)

    cv2.imshow("GRAY", result)

    print("done showing image")
    return contours

def cropImage(image):
    bwImage = convertToBW(image)
    #removeBackground(bwImage)


