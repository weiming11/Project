# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
import random as rng
import requests
import sqlite3
import schedule
import datetime
import sys
from calculate_weight2 import CalculateWeight
import imageprocessing2
import control
import notify
# initialize the camera and grab a reference to the raw camera capture
    
def setup_program():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor_pin, GPIO.OUT)
    GPIO.setup(solenoid_pin, GPIO.OUT)
    GPIO.setup(solenoid2_pin, GPIO.OUT)
    GPIO.setup(green_led_pin, GPIO.OUT)
    GPIO.setup(yellow_led_pin, GPIO.OUT)
    GPIO.setup(red_led_pin, GPIO.OUT)
    #GPIO.setup(IR_sensor,GPIO.IN)
    GPIO.setup(in1,GPIO.OUT)
    GPIO.setup(in2,GPIO.OUT)
    GPIO.setup(en,GPIO.OUT)
    
def start_program():
    control.motor_start(motor_pin)
    #GPIO.output(in1,GPIO.LOW)
    #GPIO.output(in2,GPIO.LOW)
    #p = GPIO.PWM(en,1)
    #p.start(1)
    #p.ChangeDutyCycle(100)
    control.motor2_start(in1, in2)
    control.yellow_led_on(yellow_led_pin)
    control.red_led_off(red_led_pin)
    control.green_led_off(green_led_pin)
    control.solenoid_stop(solenoid_pin)
    control.solenoid2_stop(solenoid2_pin)
    time.sleep(2)
    notify.notifySticker(34,2)
    notify.lineNotify(' weight_average: start working')

def stop_program(spearmint_count,original_count,mixfruit_count,salt_count):
    notify.lineNotify('total of "spearmint: ' + str(spearmint_count) + ' "')
    notify.lineNotify('total of "original: ' + str(original_count) + ' "')
    notify.lineNotify('total of "mixfruit: ' + str(mixfruit_count) + ' "')
    notify.lineNotify('total of "salt: ' + str(salt_count) + ' "')
    notify.lineNotify(' weight_average: Stop Working')
    control.motor_stop(motor_pin)
    control.motor2_start(in1, in2)
    control.red_led_off(red_led_pin)
    control.green_led_off(green_led_pin)
    control.yellow_led_off(yellow_led_pin)
    control.solenoid2_stop(solenoid2_pin)
    control.motor2_stop(in1, in2)
def sent_data():
    global run
    global spearmintperhour
    global originalperhour
    global mixfruitperhour
    global saltperhour
    global checkspearmint_count
    global checkoriginal_count
    global checkmixfruit_count
    global checksalt_count
    global first_time
    global time_day 
    
    date = datetime.datetime.now()
    if(first_time) == 1 :
         time_day = "D" + str(date.year) + str(date.month) + str(date.day) + "T" +  str(date.hour) + str(date.minute)
         first_time = 0
        
    date1 = str(date.year) + "-" + str(date.month) + "-" + str(date.day) + " " +  str(date.hour) + ":" + str(date.minute) + ":" + str(date.second)
    
    # สร้างออบเจ็กต์ตัวเชื่อมต่อกับฐานข้อมูล
    if(run == 0):
        conn = sqlite3.connect('%s.db' % str(time_day))
        # สร้างตาราง
        sql_create = '''
             create table %s (
                round integer,
                time text,
                id integer,
                name text,
                numberperhour integer,
                total integer 
            )
        ''' % str(time_day)# ทำตารางโปเกมอน โดยมี ๔ สดมภ์ เลข, ชื่อ, หนัก, สูง
        conn.execute(sql_create)
        run = 1
        spearmintperhour = spearmint_count
        originalperhour = original_count
        mixfruitperhour = mixfruit_count
        checkspearmint_count = spearmint_count
        checkoriginal_count = original_count
        checkmixfruit_count = mixfruit_count
        # ใส่ข้อมูลลงตาราง
        data = [(run,date1,101,'spearmint',spearmintperhour,spearmint_count),
                (run,date1,102,'original',originalperhour,original_count),
                (run,date1,103,'mixfruit',mixfruitperhour,mixfruit_count),
                (run,date1,104,'salt',saltperhour,salt_count)]

        sql_insert = '''
            insert into %s (round,time,id,name,numberperhour,total)
            values (?,?,?,?,?,?)
        ''' % str(time_day) # ข้อมูลตัวแรก
        conn.executemany(sql_insert , data)


        conn.commit() # ส่งมอบ (บันทึกความเปลี่ยนแปลง)

    elif(run >= 1):
        run = run + 1
        conn = sqlite3.connect('%s.db' % str(time_day) )
        if(spearmint_count == checkspearmint_count):
            spearmintperhour = 0
        elif(spearmint_count != checkspearmint_count):
            spearmintperhour = spearmint_count - checkspearmint_count
        if(original_count == checkoriginal_count):
            originalperhour = 0
        elif(original_count != checkoriginal_count):
            originalperhour = original_count - checkoriginal_count
        if(mixfruit_count == checkmixfruit_count):
            mixfruitperhour = 0
        elif(mixfruit_count != checkmixfruit_count):
            mixfruitperhour = mixfruit_count - checkmixfruit_count
        if(salt_count == checksalt_count):
            saltperhour = 0
        elif(salt_count != checksalt_count):
            saltperhour = salt_count - checksalt_count

        checkspearmint_count = spearmint_count
        checkoriginal_count = original_count
        checkmixfruit_count = mixfruit_count
        checksalt_count = salt_count
        
        
        data = [(run,date1,101,'spearmint',spearmintperhour,spearmint_count),
                (run,date1,102,'original',originalperhour,original_count),
                (run,date1,103,'mixfruit',mixfruitperhour,mixfruit_count),
                (run,date1,104,'salt',saltperhour,salt_count)]

        sql_insert = '''
            insert into %s (round,time,id,name,numberperhour,total)
            values (?,?,?,?,?,?)
        ''' % str(time_day) # ข้อมูลตัวแรก
        conn.executemany(sql_insert , data)
        conn.commit() 

def nothing(x):
    pass
    # ดูข้อมูล
#     sql_select = '''select * from toothpaste%s%s''' % (str(hour) , str(minute)) # เลือกเอาข้อมูลโปเกมอนทุกตัวที่ใส่ไว้
#     print("round: %d " % run)
#     for row in conn.execute(sql_select):
#         print(row) # แสดงข้อมูลทีละแถว
#         
    # ท้ายสุดแล้วต้องปิดออบเจ็กต์ตัวเชื่อมต่อทิ้ง
    conn.close()
    
EMULATE_HX711 = False
referenceUnit = -520 
if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

weight = []
weight = weight[:4]
cw = CalculateWeight(weight)
hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()


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

run = 0
spearmintperhour = 0
originalperhour = 0
mixfruitperhour = 0
saltperhour = 0
checkspearmint_count = 0
checkoriginal_count = 0
checkmixfruit_count = 0
checksalt_count = 0
first_time = 1
time_day = 0

setup_program()

start_program()

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

count_line = 0
weight_average = 0
spearmint_count = 0
original_count = 0
mixfruit_count = 0
salt_count = 0
thresh = 150
maxValue = 200
thresh1 = 100
checker = True
time.sleep(0.1)

"""cv2.namedWindow('trackbar')
cv2.createTrackbar('L_H','trackbar',0,255,nothing)
cv2.createTrackbar('L_S','trackbar',0,255,nothing)
cv2.createTrackbar('L_V','trackbar',0,255,nothing)

cv2.createTrackbar('U_H','trackbar',255,255,nothing)
cv2.createTrackbar('U_S','trackbar',255,255,nothing)
cv2.createTrackbar('U_V','trackbar',255,255,nothing)
"""
original_lower_color = np.array([90,90,90])
original_upper_color = np.array([130,255,255])
#spearmint_lower_color = np.array([69,111,135])
#spearmint_upper_color = np.array([88,251,227])
spearmint_lower_color = np.array([73,95,100])
spearmint_upper_color = np.array([89,191,173])
mixfruit_lower_color = np.array([150,0,0])
mixfruit_upper_color = np.array([190,255,255])
#salt_lower_color = np.array([70,21,117]) 
#salt_upper_color = np.array([86,65,229])
##salt_lower_color = np.array([57,25,58]) 
##salt_upper_color = np.array([84,100,255])
salt_lower_color = np.array([0,0,0]) 
salt_upper_color = np.array([255,255,255])

upper_left = (195, 160)
bottom_right = (450, 357)
cw.clear_value()


schedule.every(10).seconds.do(sent_data)
schedule.every(0.0000001).seconds.do(cw.put_weight)
# capture frames from the camera

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    
    r = cv2.rectangle(image, upper_left, bottom_right, (0,255,255), 5 )
    rect_img  = image[upper_left[1] : bottom_right[1], upper_left[0] : bottom_right[0]]
    sketcher_rect = rect_img
    cv2.namedWindow('total_toothpaste',cv2.WINDOW_AUTOSIZE)
    total_toothpaste = np.zeros((1000, 1600, 3), dtype = "uint8")
    #weight = calculate_weight.get_weight(weight)
    #val = hx.get_weight(5)
    #l_h = cv2.getTrackbarPos('L_H','trackbar')
    #l_s = cv2.getTrackbarPos('L_S','trackbar')
    #l_v = cv2.getTrackbarPos('L_V','trackbar')

    #u_h = cv2.getTrackbarPos('U_H','trackbar')
    #u_s = cv2.getTrackbarPos('U_S','trackbar')
    #u_v = cv2.getTrackbarPos('U_V','trackbar')
     
    #salt_lower_color = np.array([l_h,l_s,l_v]) 
    #salt_upper_color = np.array([u_h,u_s,u_v])
     
    #print("weight:" + str(val))
    print("weight(list):" + str(cw.get_weight1()))
    spearmint_count,weight_average,count_line,total_toothpaste = imageprocessing2.spearmint_pre_process(sketcher_rect,spearmint_count,weight_average,count_line,total_toothpaste,image,cw)
    original_count,weight_average,count_line,total_toothpaste =  imageprocessing2.original_pre_process(sketcher_rect,original_count,weight_average,count_line,total_toothpaste,image,cw)
    mixfruit_count,weight_average,count_line,total_toothpaste  = imageprocessing2.mixfruit_pre_process(sketcher_rect,mixfruit_count,weight_average,count_line,total_toothpaste,image,cw)
    salt_count,weight_average,count_line,total_toothpaste  = imageprocessing2.salt_pre_process(sketcher_rect,salt_count,weight_average,count_line,total_toothpaste,image,cw)
    
    schedule.run_pending()
    
    total_toothpaste = cv2.putText(total_toothpaste, "-Total_Toothpaste-", (300,250), cv2.FONT_HERSHEY_SIMPLEX , 3,(125,125,0), 5,cv2.LINE_AA)
    total_toothpaste = cv2.putText(total_toothpaste, "spearmint: " + str(spearmint_count) , (300,400), cv2.FONT_HERSHEY_SIMPLEX , 3,(0,255,0), 3,cv2.LINE_AA)
    total_toothpaste = cv2.putText(total_toothpaste, "original: " + str(original_count) , (300,500), cv2.FONT_HERSHEY_SIMPLEX , 3,(255,0,0), 3,cv2.LINE_AA)
    total_toothpaste = cv2.putText(total_toothpaste, "mixfruit: " + str(mixfruit_count) , (300,600), cv2.FONT_HERSHEY_SIMPLEX , 3,(0,0,255), 3,cv2.LINE_AA)
    total_toothpaste = cv2.putText(total_toothpaste, "salt: " + str(salt_count) , (300,700), cv2.FONT_HERSHEY_SIMPLEX , 3, (0,125,125), 3,cv2.LINE_AA)
    total_toothpaste = cv2.putText(total_toothpaste, "weight(3boxes): " + str(weight_average) , (300,800), cv2.FONT_HERSHEY_SIMPLEX , 3, (125,50125), 3,cv2.LINE_AA)
   
    cv2.imshow("image", image)
    cv2.imshow("total_toothpaste", total_toothpaste)
    
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        stop_program(spearmint_count,original_count,mixfruit_count,salt_count)
        break

cv2.waitKey(0)
cv2.destroyAllWindows()






















