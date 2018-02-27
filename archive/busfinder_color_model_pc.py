# USAGE
# python fps_demo.py
# python fps_demo.py --display 1

# import the necessary packages
from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from matplotlib import pyplot as plt
import numpy as np
import argparse
import imutils
import cv2

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())



# define the list of boundaries BGR
boundaries = [
#	([0,0,0], [100,255,255])
#   ([0,100,200], [10,150,252])
([0,0,0], [80,215,255])
]


# created a *threaded *video stream, allow the camera senor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()

# loop over some frames...this time using the threaded stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=400)

	# loop over the boundaries
	for (lower, upper) in boundaries:
		# create NumPy arrays from the boundaries
		lower = np.array(lower, dtype = "uint8")
		upper = np.array(upper, dtype = "uint8")

		# find the colors within the specified boundaries and apply
		# the mask
		mask = cv2.inRange(frame, lower, upper)
		output = cv2.bitwise_and(frame, frame, mask = mask)

		#img = cv2.imread('home.jpg')
		color = ('b','g','r')
		for i,col in enumerate(color):
			histr = cv2.calcHist([frame],[i],None,[256],[0,256])
			plt.plot(histr,color = col)
			plt.xlim([0,256])
		plt.show()


		# show the images
		# cv2.imshow("Frame", np.hstack([image, output]))


	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		# cv2.imshow("Frame", output)
		cv2.imshow("Frame", np.hstack([frame, output]))
		key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
