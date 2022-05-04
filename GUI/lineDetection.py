# TODO: width detection

# SOURCE: 
import cv2
import numpy as np
import os
import time

start_time = time.time()

def getLines(file_name):
    path = os.getcwd()
    base_path = path[:-3] + "vectorization/images"
    input_path = os.path.join(base_path , file_name +'.jpg')
    
    img = cv2.imread(input_path)
    # lines.png has 24 lines and 4 lines for the border
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    kernel_size = 5
    blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

    low_threshold = 50
    high_threshold = 150
    dst = cv2.Canny(blur_gray, low_threshold, high_threshold)

    rho = 40  # distance resolution in pixels of the Hough grid
    theta = 1*np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 50  # minimum number of pixels making up a line
    max_line_gap = 20  # maximum gap in pixels between connectable line segments
    line_image = np.copy(img) * 0  # creating a blank to draw lines on

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(dst, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)

    count = 0
    paths = []
    if lines is not None:
        for line in lines:
            for x1,y1,x2,y2 in line:
                #print("Line endpoints: (%s,%s), (%s,%s)",x1,y1,x2,y2)
                cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)
                paths.append([(x1,y1),(x2,y2)])
                #draw_lines_edges = cv2.addWeighted(img, 0, line_image, 1, 0)
                #name = "lines_edges_" + str(count) + ".png"
                #cv2.imwrite('lines/' + name, draw_lines_edges)
                #cv2.imshow('lines/' + name, draw_lines_edges)
                count += 1


    print("--- %s seconds ---" % (time.time() - start_time))
    print("Number of lines detected: %s" % count)

    # create image
    lines_edges = cv2.addWeighted(img, 0, line_image, 1, 0)
    #cv2.imwrite(file_name + '_lines.jpg', lines_edges)
    output_path = os.path.join(base_path , file_name +'_lines.jpg')
    cv2.imwrite(output_path, lines_edges)
    return file_name +'_lines', paths

