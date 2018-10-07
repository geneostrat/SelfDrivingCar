#!/usr/bin/env python
import Adafruit_PCA9685 as servo
import time                  # Import necessary modules

MinPulse = 200
MaxPulse = 700

def setup():
    global pwm
    pwm = servo.PCA9685()

def servo_test():
#    for value in range(MinPulse, MaxPulse):
        pwm.set_pwm_freq(60)
#        pwm.set_pwm(0, 0, 230)
#        pwm.set_pwm(14, 0, value)
#        pwm.set_pwm(15, 0, value)
#        time.sleep(2)
#        pwm.set_pwm(0, 0, 350)
#        time.sleep(2)
#        pwm.set_pwm(0, 0, 330)
#        time.sleep(2)
#        pwm.set_pwm(0, 0, 300)
#        time.sleep(2)
        pwm.set_pwm(0, 0, 340)
        time.sleep(2)
        pwm.set_pwm(0, 0, 350)
        time.sleep(2)
        pwm.set_pwm(0, 0, 360)
        time.sleep(2)
        pwm.set_pwm(0, 0, 380)
        time.sleep(2)
        pwm.set_pwm(0, 0, 410) # center?
        time.sleep(2)
        pwm.set_pwm(0, 0, 440)
        time.sleep(2)
        pwm.set_pwm(0, 0, 480) 
        time.sleep(2)
        pwm.set_pwm(0, 0, 410) # center?
        time.sleep(2)
        pwm.set_pwm(0, 0, 400) # center?
        
        
if __name__ == '__main__':
    setup()
    servo_test()
