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

def convertToBW(image_name):
    img = cv2.imread(image_name)
    h, w, c = img.shape
    contourIm = img.copy()
    grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    (thresh, blackAndWhiteImage) = cv2.threshold(grayImage, 150, 255, cv2.THRESH_BINARY)
    #filter noise
    kernel = np.ones((10,10),np.uint8)
    result = cv2.morphologyEx(blackAndWhiteImage, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy  = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print("len", len(contours))
    #contours = contours[0] if len(contours) == 2 else contours[1]
    big_contour = max(contours, key=cv2.contourArea)

    # draw white contour on black background as mask
    mask = np.zeros((h,w), dtype=np.uint8)
    cv2.drawContours(mask, [big_contour], 0, (255,255,255), cv2.FILLED)

    # invert mask so shapes are white on black background
    mask_inv = 255 - mask

    # create new (blue) background
    bckgnd = np.full_like(img, (255,0,0))

    # apply mask to image
    image_masked = cv2.bitwise_and(img, img, mask=mask)

    # apply inverse mask to background
    bckgnd_masked = cv2.bitwise_and(bckgnd, bckgnd, mask=mask_inv)

    # add together
    result = cv2.add(image_masked, bckgnd_masked)

    #cv2.imshow("GRAY", result)
    #cv2.waitKey(0)

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


