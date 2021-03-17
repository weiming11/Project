import RPi.GPIO as GPIO
import time



def motor_stop(motor_pin):
    GPIO.output(motor_pin,GPIO.HIGH)
    
def motor_start(motor_pin):
    GPIO.output(motor_pin,GPIO.LOW)
    
def motor2_stop(in1,in2):
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
     
def motor2_start(in1,in2):
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    
def solenoid_start(solenoid_pin):
    GPIO.output(solenoid_pin,GPIO.LOW)
    time.sleep(2)
    
def solenoid_stop(solenoid_pin):
    GPIO.output(solenoid_pin,GPIO.HIGH)
    time.sleep(2)
    
def solenoid2_stop(solenoid2_pin):
    GPIO.output(solenoid2_pin,GPIO.LOW)
    time.sleep(2)
    
def solenoid2_start(solenoid2_pin):
    GPIO.output(solenoid2_pin,GPIO.HIGH)
    time.sleep(2)
    
def yellow_led_off(yellow_led_pin):
    GPIO.output(yellow_led_pin,GPIO.HIGH)
    
def yellow_led_on(yellow_led_pin):
    GPIO.output(yellow_led_pin,GPIO.LOW)
    
def green_led_off(green_led_pin):
    GPIO.output(green_led_pin,GPIO.HIGH)
    
def green_led_on(green_led_pin):
    GPIO.output(green_led_pin,GPIO.LOW)
    
def red_led_off(red_led_pin):
    GPIO.output(red_led_pin,GPIO.HIGH)
    
def red_led_on(red_led_pin):
    GPIO.output(red_led_pin,GPIO.LOW)
