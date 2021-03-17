import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import random as rng
import requests
import sqlite3
import time
import schedule
import datetime
from calculate_weight2 import CalculateWeight
import control
import notify

motor_pin = 16
solenoid_pin = 24
solenoid2_pin = 12
green_led_pin = 17
yellow_led_pin = 27
red_led_pin = 22
IR_sensor = 21
in1 = 20
in2 = 23
en = 13
temp1=1


original_lower_color = np.array([90,90,90])
original_upper_color = np.array([130,255,255])
spearmint_lower_color = np.array([69,111,135])
spearmint_upper_color = np.array([88,251,227])
mixfruit_lower_color = np.array([150,0,0])
mixfruit_upper_color = np.array([190,255,255])
salt_lower_color = np.array([70,21,117]) 
salt_upper_color = np.array([84,65,229])

def spearmint_pre_process(image,spearmint_count,weight_average,count_line,total_toothpaste,image2,cw):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, spearmint_lower_color, spearmint_upper_color)
    kernal = np.ones((5, 5), "uint8") 
    mask = cv2.dilate(mask, kernal) 
    res = cv2.bitwise_and(image, image, mask=mask)
    gray_blur = cv2.GaussianBlur(res,(7,7),0)
    gray = cv2.cvtColor(gray_blur, cv2.COLOR_BGR2GRAY)
    spearmint_count,weight_average,count_line,total_toothpaste = thresh_callback1(gray,spearmint_count,weight_average,count_line,total_toothpaste,image2,cw )
    return spearmint_count,weight_average,count_line,total_toothpaste


def original_pre_process(image,original_count,weight_average,count_line,total_toothpaste,image2,cw ):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, original_lower_color, original_upper_color)
    kernal = np.ones((5, 5), "uint8") 
    mask = cv2.dilate(mask, kernal)
    res = cv2.bitwise_and(image, image, mask=mask)
    gray_blur = cv2.GaussianBlur(res,(7,7),0)
    gray = cv2.cvtColor(gray_blur, cv2.COLOR_BGR2GRAY)
    original_count,weight_average,count_line,total_toothpaste  = thresh_callback2(gray,original_count,weight_average,count_line,total_toothpaste,image2,cw  )
    return original_count,weight_average,count_line,total_toothpaste

def mixfruit_pre_process(image,mixfruit_count,weight_average,count_line,total_toothpaste,image2,cw ):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, mixfruit_lower_color, mixfruit_upper_color)
    kernal = np.ones((5, 5), "uint8") 
    mask = cv2.dilate(mask, kernal) 
    res = cv2.bitwise_and(image, image, mask=mask)
    gray_blur = cv2.GaussianBlur(res,(7,7),0)
    gray = cv2.cvtColor(gray_blur, cv2.COLOR_BGR2GRAY)
    mixfruit_count,weight_average,count_line,total_toothpaste = thresh_callback3(gray,mixfruit_count,weight_average,count_line,total_toothpaste,image2,cw  )
    return mixfruit_count,weight_average,count_line,total_toothpaste

def salt_pre_process(image,salt_count,weight_average,count_line,total_toothpaste,image2,cw ):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, salt_lower_color, salt_upper_color)
    kernal = np.ones((5, 5), "uint8") 
    mask = cv2.dilate(mask, kernal) 
    res = cv2.bitwise_and(image, image, mask=mask)
    gray_blur = cv2.GaussianBlur(res,(7,7),0)
    gray = cv2.cvtColor(gray_blur, cv2.COLOR_BGR2GRAY)
    salt_count,weight_average,count_line,total_toothpaste = thresh_callback4(gray,salt_count,weight_average,count_line,total_toothpaste,image,cw  )
    return salt_count,weight_average,count_line,total_toothpaste
    

def sobel_filter(gray):
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S
    
    grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    

    
    grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
    
    return grad

def thresh_callback1(gray,spearmint_count,weight_average,count_line,total_toothpaste,image,cw  ):
    threshold = 60
     
    canny_output = sobel_filter(gray)
    canny_output = cv2.adaptiveThreshold(canny_output,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    centers = [None]*len(contours)
    radius = [None]*len(contours)
    blobs = []
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
        x,y,w,h = boundRect[i]
        if(w > 200 and w < 230 and h > 156 and h < 187):
            print("width:" , w , "height:" , h)
            
            blobs.append(boundRect[i])
            control.motor_stop(motor_pin)
            control.solenoid2_start(solenoid2_pin)
            control.yellow_led_off(yellow_led_pin)
            time.sleep(1)
            weight_average,weight =  cw.th()
            if(float(weight_average) < 206):
                weight_average,weight =   cw.th()
            if(float(weight[4]) > 207 and float(weight[4]) < 220):
                weight_average = weight[4]
            #weight_average = cw.get_weight1()
            
            print('3boxes: ' + str(weight_average) + ' (spearmint)')
            total_toothpaste  = cv2.putText(total_toothpaste , "weight(3boxes): " + str(weight_average) , (300,800), cv2.FONT_HERSHEY_SIMPLEX , 3,(125,50125), 3,cv2.LINE_AA)
            cv2.imshow("total_toothpaste", total_toothpaste)
            cv2.waitKey(1)
            if(float(weight_average) < 207):
                control.red_led_on(red_led_pin)
                control.motor_stop(motor_pin)
                if(count_line == 0):
                    notify.notify_error(weight_average)
                count_line = 1

            else:
                spearmint_count += 3
                control.red_led_off(red_led_pin)
                control.green_led_on(green_led_pin)
                control.motor_stop(motor_pin)
                
                time.sleep(1)
                
                control.solenoid_start(solenoid_pin)
                control.solenoid_stop(solenoid_pin)
                control.solenoid2_stop(solenoid2_pin)
                control.motor_start(motor_pin)
                control.green_led_off(green_led_pin)
                control.yellow_led_on(yellow_led_pin)
                
                count_line = 0
            
                
        centers[i], radius[i] = cv2.minEnclosingCircle(contours_poly[i])
    
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    
    
    for i in range(len(blobs)):
        color = (0,255,0)
        cv2.rectangle(image, (int(blobs[i][0]+215), int(blobs[i][1]+170)),(int(blobs[i][0]+blobs[i][2]+215), int(blobs[i][1]+blobs[i][3]+170)), color, 2)

    return spearmint_count,weight_average,count_line,total_toothpaste

def thresh_callback2(gray,original_count,weight_average,count_line,total_toothpaste,image,cw  ):
    threshold = 60
     
    canny_output = sobel_filter(gray)
    canny_output = cv2.adaptiveThreshold(canny_output,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    centers = [None]*len(contours)
    radius = [None]*len(contours)
    blobs = []
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
        x,y,w,h = boundRect[i]
        
        if(w > 200 and w < 230 and h > 156 and h < 187):
            print("width:" , w , "height:" , h)
            blobs.append(boundRect[i])
            control.motor_stop(motor_pin)
            control.solenoid2_start(solenoid2_pin)
            control.yellow_led_off(yellow_led_pin)
            time.sleep(1)
            weight_average,weight = cw.th()
            if(float(weight_average)  < 206):
                weight_average,weight =   cw.th()
            if(float(weight[4]) > 207 and float(weight[4]) < 220):
                weight_average = weight[4]
#             weight_average = cw.get_weight1()
            
            print('3boxes: ' + str(weight_average) + '(original)')
            total_toothpaste  = cv2.putText(total_toothpaste , "weight(3boxes): " + str(weight_average) , (300,800), cv2.FONT_HERSHEY_SIMPLEX , 3,(125,50125), 3,cv2.LINE_AA)
            cv2.imshow("total_toothpaste", total_toothpaste)
            cv2.waitKey(1)
            if(float(weight_average) < 207):
                control.red_led_on(red_led_pin)
                control.motor_stop(motor_pin)
                if(count_line == 0):
                    notify.notify_error(weight_average)
                count_line = 1
        
            else:
                original_count += 3
                control.red_led_off(red_led_pin)
                control.green_led_on(green_led_pin)
                control.motor_stop(motor_pin)
            
                time.sleep(1)
                
                control.solenoid_start(solenoid_pin)
                control.solenoid_stop(solenoid_pin)
                control.solenoid2_stop(solenoid2_pin)
                control.motor_start(motor_pin)
                control.green_led_off(green_led_pin)
                control.yellow_led_on(yellow_led_pin)
                count_line = 0
        
           
        centers[i], radius[i] = cv2.minEnclosingCircle(contours_poly[i])
    
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    
    
    for i in range(len(blobs)):
        color = (255,0,0)
        cv2.rectangle(image, (int(blobs[i][0]+215), int(blobs[i][1]+170)),(int(blobs[i][0]+blobs[i][2]+215), int(blobs[i][1]+blobs[i][3]+170)), color, 2)
    return original_count,weight_average,count_line,total_toothpaste

def thresh_callback3(gray,mixfruit_count,weight_average,count_line,total_toothpaste,image,cw  ):
    threshold = 60
    canny_output = sobel_filter(gray)
    canny_output = cv2.adaptiveThreshold(canny_output,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    centers = [None]*len(contours)
    radius = [None]*len(contours)
    blobs = []
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
        x,y,w,h = boundRect[i]
        if(w > 200 and w < 230 and h > 156 and h < 187):
            print("width:" , w , "height:" , h)
            blobs.append(boundRect[i])
            control.motor_stop(motor_pin)
            control.solenoid2_start(solenoid2_pin)
            control.yellow_led_off(yellow_led_pin)
            time.sleep(1)
            weight_average,weight =  cw.th()
            if(float(weight_average)  < 206):
                weight_average,weight =   cw.th()
            if(float(weight[4]) > 207 and float(weight[4]) < 220):
                weight_average = weight[4]
#             weight_average = cw.get_weight1()
            
            print('3boxes' + str(weight_average) + ' (mixfruit)')
    
            total_toothpaste = cv2.putText(total_toothpaste, "weight(3boxes): " + str(weight_average) , (300,800), cv2.FONT_HERSHEY_SIMPLEX , 3,(125,50125), 3,cv2.LINE_AA)
            cv2.imshow("total_toothpaste", total_toothpaste)
            cv2.waitKey(1)
            if(float(weight_average) < 207):
                control.red_led_on(red_led_pin)
                control.motor_stop(motor_pin)
                if(count_line == 0):
                    notify.notify_error(weight_average)
                count_line = 1
                               
            else:
                mixfruit_count += 3
                control.red_led_off(red_led_pin)
                control.green_led_on(green_led_pin)
                control.motor_stop(motor_pin)
                
                time.sleep(1)
                
                control.solenoid_start(solenoid_pin)
                control.solenoid_stop(solenoid_pin)
                control.solenoid2_stop(solenoid2_pin)
                control.motor_start(motor_pin)
                control.green_led_off(green_led_pin)
                control.yellow_led_on(yellow_led_pin)
                count_line = 0
            
           
        centers[i], radius[i] = cv2.minEnclosingCircle(contours_poly[i])
    
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    
    
    for i in range(len(blobs)):
        color = (0,0,255)
        cv2.rectangle(image, (int(blobs[i][0]+215), int(blobs[i][1]+170)),(int(blobs[i][0]+blobs[i][2]+215), int(blobs[i][1]+blobs[i][3]+170)), color, 2)
    return mixfruit_count,weight_average,count_line,total_toothpaste


def thresh_callback4(gray,salt_count,weight_average,count_line,total_toothpaste,image,cw  ):
    
    threshold = 60
    canny_output = sobel_filter(gray)
    canny_output = cv2.adaptiveThreshold(canny_output,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
    contours, hierarchy = cv2.findContours(canny_output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cv2.imshow("salt", canny_output)
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    centers = [None]*len(contours)
    radius = [None]*len(contours)
    blobs = []
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
        x,y,w,h = boundRect[i]
        #print("width:" , w , "height:" , h)
        if(w > 200 and w < 230 and h > 156 and h < 187):
            print("width:" , w , "height:" , h)
            blobs.append(boundRect[i])
            control.motor_stop(motor_pin)
            control.solenoid2_start(solenoid2_pin)
            control.yellow_led_off(yellow_led_pin)
            time.sleep(1)
            weight_average,weight =   cw.th()
            if(float(weight_average)  < 206):
                weight_average,weight =   cw.th()
            if(float(weight[4]) > 207 and float(weight[4]) < 220):
                weight_average = weight[4]
            #weight_average = cw.get_weight1()
            print('3boxes: ' + str(weight_average) + ' (salt)')
            
            total_toothpaste = cv2.putText(total_toothpaste, "weight(3boxes): " + str(weight_average) , (300,800), cv2.FONT_HERSHEY_SIMPLEX , 3,(125,50125), 3,cv2.LINE_AA)
            cv2.imshow("total_toothpaste", total_toothpaste)
            cv2.waitKey(1)
            
            if(float(weight_average) < 207):
                control.red_led_on(red_led_pin)
                control.motor_stop(motor_pin)
                if(count_line == 0):
                    notify.notify_error(weight_average)
                count_line = 1
            
            else:
                salt_count += 3
                control.red_led_off(red_led_pin)
                control.green_led_on(green_led_pin)
                control.motor_stop(motor_pin)
                
                time.sleep(1)
        
                control.solenoid_start(solenoid_pin)
                control.solenoid_stop(solenoid_pin)
                control.solenoid2_stop(solenoid2_pin)
                control.motor_start(motor_pin)
                control.green_led_off(green_led_pin)
                control.yellow_led_on(yellow_led_pin)
                count_line = 0
            
           
        centers[i], radius[i] = cv2.minEnclosingCircle(contours_poly[i])
    
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    
    
    for i in range(len(blobs)):
        color = (255,255,255)
        cv2.rectangle(image, (int(blobs[i][0]+215), int(blobs[i][1]+170)),(int(blobs[i][0]+blobs[i][2]+215), int(blobs[i][1]+blobs[i][3]+170)), color, 2)
    #cv2.imshow("imageasd", image)
    return salt_count,weight_average,count_line,total_toothpaste

