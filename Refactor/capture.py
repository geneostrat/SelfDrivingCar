import Adafruit_PCA9685 as servo
import RPi.GPIO as GPIO
import time                  
import evdev
from evdev import InputDevice, categorize, ecodes
from picamera import PiCamera
import os
import _thread
import sys
import carcommon as car

# ===========================================================================
# Acquire the gamepad controller
# ===========================================================================

#creates object gamepad
gamepad = InputDevice('/dev/input/event0')

FORWARD_SPEED = 37

currentSteerFreqHz = 410 # center
counter = 0
continueCapture = True

car.setup()
car.TRIAL = input('Enter trial name:')
car.setup_capture()

car.setupMotor()
car.setSpeed(FORWARD_SPEED)

#print out device info at start
print(gamepad)
car.stop()

aBtn = 289
bBtn = 290
xBtn = 288
yBtn = 291
lBtn = 292
rBtn = 293
selBtn = 296
staBtn = 297

j = 0
#display codes
for event in gamepad.read_loop():
    # buttons 
    j += 1
    if event.type == ecodes.EV_KEY:
        #print(event)
        if event.value == 1:
            if event.code == xBtn:
                print("X")
            elif event.code == bBtn:
                print("B")
            elif event.code == aBtn:
                print("A")
                car.CONTINUE_CAPTURE = False
                car.stop()
                sys.exit('completed capture')
            elif event.code == yBtn:
                print("Y")
                car.backward()
                _thread.start_new_thread(car.threadCapture, (counter,))
            elif event.code == lBtn:
                print("LEFT")
            elif event.code == rBtn:
                print("RIGHT")
            elif event.code == selBtn:
                print("Select")
            elif event.code == staBtn:
                print("Start")
        elif event.value == 0:
          print("Release")

    # Analog gamepad
    elif event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        if ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_Z":
             currentSteer = 273+absevent.event.value
             car.currentSteerFreqHz = currentSteer
             car.get_pwm().set_pwm(0, 0, currentSteer)


