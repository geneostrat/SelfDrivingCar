import Adafruit_PCA9685 as servo
import time                  # Import necessary modules
import evdev
from evdev import InputDevice, categorize, ecodes

def setup():
    global pwm
    pwm = servo.PCA9685()
    pwm.set_pwm_freq(60)

#creates object gamepad
gamepad = InputDevice('/dev/input/event0')

setup()

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

#display codes
for event in gamepad.read_loop():
    # buttons 
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
        '''elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_RZ":
             print("Y", absevent.event.value)
             if absevent.event.value == 0:
                print("Up")
             elif absevent.event.value == 255:
                print("Down")
             elif absevent.event.value == 127:
                print("Center")'''

