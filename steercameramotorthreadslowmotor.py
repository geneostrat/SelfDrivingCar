import Adafruit_PCA9685 as servo
import RPi.GPIO as GPIO
import time                  
import evdev
from evdev import InputDevice, categorize, ecodes
from picamera import PiCamera
import os
import _thread

# ===========================================================================
# Raspberry Pi pin11, 12, 13 and 15 to realize the clockwise/counterclockwise
# rotation and forward and backward movements
# ===========================================================================
Motor0_A = 11  # pin11
Motor0_B = 12  # pin12
Motor1_A = 13  # pin13
Motor1_B = 15  # pin15

# ===========================================================================
# Set channel 4 and 5 of the servo driver IC to generate PWM, thus 
# controlling the speed of the car
# ===========================================================================
EN_M0    = 4  # servo driver IC CH4
EN_M1    = 5  # servo driver IC CH5

pins = [Motor0_A, Motor0_B, Motor1_A, Motor1_B]

# ===========================================================================
# Camera configuration
# ===========================================================================

TRIAL = 109
CAPTURE_DIR = 'car'
FRAME_H = 90
FRAME_W = 180
SHUTTER_SPEED = 800
FRAME_RATE = 90

# ===========================================================================
# Camera capture setup
# ===========================================================================

def setup():
    global pwm
    pwm = servo.PCA9685()
    pwm.set_pwm_freq(60)
    global camera
    camera = PiCamera(resolution=(FRAME_H,FRAME_W)) #, framerate=FRAME_RATE)
    camera.video_stabilization = False
    camera.framerate = 30
    #camera.shutter_speed = SHUTTER_SPEED
'''    camera.framerate = 30
    camera.ISO = 400
    camera.brightness = 50
    camera.saturation = 0
    camera.sharpness = 0
    camera.brightness = 0
    camera.shutter_speed = 1000 '''

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

# ===========================================================================
# Steering file
# ===========================================================================

def write_steer(counter, offset):
    filename = CAPTURE_DIR + '/' + str(TRIAL) + '/steer/' + str(counter) + '.txt'
    with open(filename, 'w') as file:
        file.write(str(offset))

# ===========================================================================
# Adjust the duty cycle of the square waves output from channel 4 and 5 of
# the servo driver IC, so as to control the speed of the car.
# ===========================================================================
def setSpeed(speed):
	speed *= 40
	print ('speed is: ', speed)
	pwm.set_pwm(EN_M0, 0, speed)
	pwm.set_pwm(EN_M1, 0, speed)

def setupMotor(busnum=None):
	global forward0, forward1, backward1, backward0
#	global pwm
#	if busnum == None:
#		pwm = p.PCA9685()               # Initialize the servo controller.
#	else:
#		pwm = p.PWM(bus_number=busnum) # Initialize the servo controller.

	pwm.frequency = 60
	forward0 = 'True'
	forward1 = 'True'
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)        # Number GPIOs by its physical location
	try:
		for line in open("config"):
			if line[0:8] == "forward0":
				forward0 = line[11:-1]
			if line[0:8] == "forward1":
				forward1 = line[11:-1]
	except:
		pass
	if forward0 == 'True':
		backward0 = 'False'
	elif forward0 == 'False':
		backward0 = 'True'
	if forward1 == 'True':
		backward1 = 'False'
	elif forward1 == 'False':
		backward1 = 'True'
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)   # Set all pins' mode as output

# ===========================================================================
# Control the DC motor to make it rotate clockwise, so the car will 
# move forward.
# ===========================================================================

def motor0(x):
	if x == 'True':
		GPIO.output(Motor0_A, GPIO.LOW)
		GPIO.output(Motor0_B, GPIO.HIGH)
	elif x == 'False':
		GPIO.output(Motor0_A, GPIO.HIGH)
		GPIO.output(Motor0_B, GPIO.LOW)
	else:
		print ('Config Error')

def motor1(x):
	if x == 'True':
		GPIO.output(Motor1_A, GPIO.LOW)
		GPIO.output(Motor1_B, GPIO.HIGH)
	elif x == 'False':
		GPIO.output(Motor1_A, GPIO.HIGH)
		GPIO.output(Motor1_B, GPIO.LOW)

def forward():
	motor0(forward0)
	motor1(forward1)

def backward():
	motor0(backward0)
	motor1(backward1)

def forwardWithSpeed(spd = 50):
	setSpeed(spd)
	motor0(forward0)
	motor1(forward1)

def backwardWithSpeed(spd = 50):
	setSpeed(spd)
	motor0(backward0)
	motor1(backward1)

def stop():
	for pin in pins:
		GPIO.output(pin, GPIO.LOW)

def threadCapture(counter):
    print('in thread')
    while continueCapture == True:
        write_steer(counter, currentSteerFreqHz)
        counter = frame_grab(counter)
    print('out of thread')

#creates object gamepad
gamepad = InputDevice('/dev/input/event0')

currentSteerFreqHz = 410 # center
counter = 0
continueCapture = True

setup()
setup_capture()

setupMotor()
setSpeed(35) #50)

#print out device info at start
print(gamepad)
stop()

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
                continueCapture = False
                stop()
            elif event.code == yBtn:
                print("Y")
                backward()
                _thread.start_new_thread(threadCapture, (counter,))
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
             currentSteerFreqHz = 273+absevent.event.value
             pwm.set_pwm(0, 0, currentSteerFreqHz)
#             if (j > 30):
#                 write_steer(counter, 273+absevent.event.value)
#                 counter = frame_grab(counter)
#                 j = 0
             
        '''elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_RZ":
             print("Y", absevent.event.value)
             if absevent.event.value == 0:
                print("Up")
             elif absevent.event.value == 255:
                print("Down")
             elif absevent.event.value == 127:
                print("Center")'''

