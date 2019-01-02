from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2
import time

FRAME_H = 90
FRAME_W = 180

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (FRAME_W, FRAME_H)
camera.framerate = 50
rawCapture = PiRGBArray(camera, size=(FRAME_W, FRAME_H))
time.sleep(0.1)
counter = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# Grab the raw NumPy array representing the image
	image = frame.array # cv2.flip(frame.array, 0)
	cv2.imshow("Frame", image)

	imageresized = cv2.resize(image, (FRAME_W, FRAME_H), interpolation = cv2.INTER_CUBIC)

	#cv2.imwrite('demo/image/' + str(counter).zfill(6) + '.png', image)
	#with open('demo/steer/' + str(counter).zfill(6) + '.txt', 'w') as steer_file:
        #    steer_file.write(str(steer*10))
	counter += 1

	# Clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	key = cv2.waitKey(1) & 0xFF
 
	# If the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
