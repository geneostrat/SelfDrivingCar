import Adafruit_PCA9685 as servo
import RPi.GPIO as GPIO
from picamera.array import PiRGBArray
from evdev import InputDevice, categorize, ecodes
from picamera import PiCamera
import time
import cv2
import os
import math
import threading
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras

import carcommon as car

RECORD = False

STEER_MIDPT = 410.
STEER_UPPER = 480.
STEER_LOWER = 340.

# ===========================================================================
# Utility methods
# ===========================================================================

def normalize(image):
    image = image.astype('float32')
    image -= np.mean(image, axis=(0,1))
    image /= np.std( image, axis=(0,1))

    return image

def custom_loss(y_true, y_pred):
    loss = tf.square(y_true - y_pred)
    loss = .5 * tf.reduce_mean(loss)
    return loss
 
customObjects =  {
    "custom_loss": custom_loss
}

print('begin model load...')
model = keras.models.load_model('weights12-7-18.hdf5', custom_objects=customObjects)       # well defined model with good training data
#model = keras.models.load_model('weights11-11-18.hdf5', custom_objects=customObjects)     # poorly defined model with good training data
#model = keras.models.load_model('weightsLane11-24-18.hdf5', custom_objects=customObjects) # poorly defined model with poor training data
print('model loaded')

# ===========================================================================
# Initialize of camera and drive system
# ===========================================================================
car.setup()
rawCapture = PiRGBArray(car.camera, size=(car.FRAME_W, car.FRAME_H))
time.sleep(0.1)
counter = 0

print('Calibrated steering - centered now')
car.setupMotor()
car.get_pwm().set_pwm(0, 0, 410)

FORWARD_SPEED = int(input('Enter speed (minimum is about 37):'))
car.setSpeed(FORWARD_SPEED)
car.backward() # yes, the motors are wired in reverse!

# ===========================================================================
# Drive loop
# ===========================================================================
try:
  for frame in car.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  
      # Grab the raw NumPy array representing the image
      image = frame.array 
      #cv2.imshow("Frame", image) -- if executing from an X-Server this will show the camera's view
  
      # Pre-process the image 
      net_inp = np.expand_dims(normalize(image[:]), 0)
      
      # Drum roll please... here is where the magic happens!
      net_out = model.predict(net_inp)[0][0]
      #print('predicted angle ', net_out)
  
      # Send PWM signal to servo
      if math.isnan(net_out) == False:
          steer = int(net_out * (STEER_UPPER - STEER_MIDPT) + STEER_MIDPT)
          # print ('Predicted Angle:', steer)
          car.get_pwm().set_pwm(0, 0, steer)
  
      # additional training data can be collected by writing the self-driving results
      if RECORD: 
              cv2.imwrite('demo/image/' + str(counter).zfill(6) + '.png', image)
              with open('demo/steer/' + str(counter).zfill(6) + '.txt', 'w') as steer_file:
                  steer_file.write(str(steer*10))
              counter += 1
  
      # Clear the stream in preparation for the next frame
      rawCapture.truncate(0)
  
      # If the `q` key was pressed, break from the loop
      key = cv2.waitKey(1) & 0xFF
      if key == ord("q"):
          print('quit - stopping car')
          car.stop()
          break
except:
    print('stopping car')
    car.stop()
    
