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

TRIAL = 'CAPTURE'
CAPTURE_DIR = 'car'
FRAME_H = 90
FRAME_W = 180
SHUTTER_SPEED = 800
FRAME_RATE = 90

# ===========================================================================
# Drive speed default value
# ===========================================================================

FORWARD_SPEED = 37

# ===========================================================================
# Establish current steering value
# ===========================================================================

currentSteerFreqHz = 410 # center

# ===========================================================================
# Capture loop
# ===========================================================================

CONTINUE_CAPTURE = True

# ===========================================================================
# Camera capture setup
# ===========================================================================

def setup():
    global pwm
    pwm = servo.PCA9685()
    pwm.set_pwm_freq(60)
    global camera
    camera = PiCamera(resolution=(FRAME_W,FRAME_H)) #, framerate=FRAME_RATE)
    camera.video_stabilization = False
    camera.framerate = 30

def setup_capture():
    os.system('mkdir ' + CAPTURE_DIR)
    os.system('mkdir ' + CAPTURE_DIR + '/' + str(TRIAL))  
    os.system('mkdir ' + CAPTURE_DIR + '/' + str(TRIAL) + '/image')
    os.system('mkdir ' + CAPTURE_DIR + '/' + str(TRIAL) + '/steer')

def frame_grab(counter):
    filename = CAPTURE_DIR + '/' + str(TRIAL) + '/image/' + str(TRIAL) + '_' + str(counter) + '.jpg'
    counter += 1
    camera.start_preview()
    camera.capture(filename, 'jpeg', use_video_port = True)
    return counter

def setup_pwm():
    global pwm
    pwm = servo.PCA9685()
    pwm.set_pwm_freq(60)
    
# ===========================================================================
# Steering file
# ===========================================================================

def write_steer(counter, offset):
    filename = CAPTURE_DIR + '/' + str(TRIAL) + '/steer/' + str(TRIAL) + '_' +  str(counter) + '.txt'
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

def set_current_steer(freq):
    currentSteerFreqHz = freq

def threadCapture(counter):
    print('in thread')
    while CONTINUE_CAPTURE == True:
        write_steer(counter, currentSteerFreqHz)
        counter = frame_grab(counter)
    print('out of thread')

def get_pwm():
    return pwm

 