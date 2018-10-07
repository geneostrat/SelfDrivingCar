import Adafruit_PCA9685 as servo
import time                  # Import necessary modules
import evdev
from evdev import InputDevice, categorize, ecodes
from picamera import PiCamera
import os

TRIAL = 2
CAPTURE_DIR = 'car'
FRAME_H = 90
FRAME_W = 180
SHUTTER_SPEED = 800
FRAME_RATE = 90

def setup():
    global pwm
    pwm = servo.PCA9685()
    pwm.set_pwm_freq(60)
    global camera
    camera = PiCamera(resolution=(FRAME_H,FRAME_W)) #, framerate=FRAME_RATE)
    camera.video_stabilization = True
    camera.shutter_speed = SHUTTER_SPEED

def setup_capture():
    os.system('mkdir ' + CAPTURE_DIR)
    os.system('mkdir ' + CAPTURE_DIR + '/' + str(TRIAL))  
    os.system('mkdir ' + CAPTURE_DIR + '/' + str(TRIAL) + '/image')
    os.system('mkdir ' + CAPTURE_DIR + '/' + str(TRIAL) + '/steer')

def frame_grab(counter):
    filename = CAPTURE_DIR + '/' + str(TRIAL) + '/image/' + str(counter) + '.jpg'
    counter += 1
    camera.start_preview()
    camera.capture(filename, 'jpeg', use_video_port = True)
    return counter

def write_steer(counter, offset):
    filename = CAPTURE_DIR + '/' + str(TRIAL) + '/steer/' + str(counter) + '.txt'
    with open(filename, 'w') as file:
        file.write(str(offset))

#creates object gamepad
gamepad = InputDevice('/dev/input/event0')

counter = 0
setup()
setup_capture()
counter = frame_grab(counter)
counter = frame_grab(counter)

#print out device info at start
print(gamepad)

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
            elif event.code == yBtn:
                print("Y")
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
        #print ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value
        if ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_Z":
             pwm.set_pwm(0, 0, 273+absevent.event.value)
             if (j > 30):
                 write_steer(counter, 273+absevent.event.value)
                 counter = frame_grab(counter)
                 j = 0
             
        '''elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_RZ":
             print("Y", absevent.event.value)
             if absevent.event.value == 0:
                print("Up")
             elif absevent.event.value == 255:
                print("Down")
             elif absevent.event.value == 127:
                print("Center")'''

