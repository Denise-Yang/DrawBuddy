#script for cropping image and extracting the white paper
#Denise Yang
#https://stackoverflow.com/questions/64295209/removing-background-around-contour
#https://stackoverflow.com/questions/63001988/how-to-remove-background-of-images-in-python
#https://stackoverflow.com/questions/60794387/detect-white-rectangle-on-black-white-image-and-crop-opencv
import cv2 
import numpy as np
def show_image(image):
    cv2.imshow('image',image)
    c = cv2.waitKey()
    if c >= 0 : return -1
    return 0
def scaleRect(x,y,w,h, scale):
    cx = x+ w/2
    cy = y + h/2
    newh = h*scale
    neww = w*scale
    return int(cx - neww/2), int(cy - newh/2), int(neww), int(newh)
def resize(img, cnt, w,h):
    
    #Create a rectangle around contour region of interest
    epsilon = 0.1*cv2.arcLength(cnt,True)
    approx = cv2.approxPolyDP(cnt,epsilon,True)
    x,y,w1,h1 = cv2.boundingRect(approx)
    #scale the image to remove the hand
    x1,y1,w1,h1 = scaleRect(x,y,w1,h1,.8)
    cropped_im = img[y1:y1+h1, x1:x1+w1]
    return cropped_im
def cropImage(image_name):
    img = cv2.imread(image_name)
    h, w, c = img.shape
    contourIm = img.copy()
    grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 150, 255, cv2.THRESH_BINARY)
    #filter noise
    
    kernel = np.ones((10,10),np.uint8)
    result = cv2.morphologyEx(blackAndWhiteImage, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy  = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    #draw rectangle
    #contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)
    cropped_im = resize(contourIm, big_contour, w, h)
    return cropped_im
