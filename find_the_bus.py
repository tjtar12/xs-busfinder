###############################################################
#	Title:  	Find The Bus!
#	Author: 	Thomas Tar
#	Company: 	FusionStorm
#
#	Credit:		PyImageSearch (multiple code bases)
#
#	USAGE
# 	python find_the_bus.py
# 	python find_the_bus.py --video samples/bus_trials.mp4
###############################################################


# IMPORT ALL PACKAGES
import numpy as np
import argparse
import datetime
import imutils
import time
import cv2
import os
import boto3
from slackclient import SlackClient



# GRAB CMD LINE ARGUMENTS
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# DEFINE TOKENS (SUPPLIED AT RUNTIME)
slack_token = os.environ.get('SLACK_API_TOKEN')
aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

# INITIALIZE SLACK
sc = SlackClient(slack_token)

# POST TO SLACK THAT APP IS STARTING
sc.api_call(
  "chat.postMessage",
  channel="#schoolbus",
  text="Bus Monitoring is on :tada:"
)

s3 = boto3.client(
	's3',
	aws_access_key_id=aws_access_key,
	aws_secret_access_key=aws_secret_access_key
)

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(2.00)
# otherwise, we are reading from a video file
else:
	camera = cv2.VideoCapture(args["video"])

# initialize the first frame in the video stream
firstFrame = None

# loop over the frames of the video
while True:
	timestamp = datetime.datetime.now()
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")

	# grab the current frame and initialize the occupied/unoccupied
	# text
	(grabbed, frame) = camera.read()
	text = ""

	# if the frame could not be grabbed, then we have reached the end
	# of the video
	if not grabbed:
		break

	cv2.imshow("Bus Finder - Wide Angle", frame)

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)

	cv2.imshow("Bus Finder - Wide Angle", frame)

	if args.get("video", None) is None:
		crop_img = frame[90:220, 220:360]
	else:
		crop_img = frame[50:150, 150:300]

	#cv2.imshow("Crop Test", crop_img)

	#frame = crop_img
	frame = imutils.resize(crop_img, width=500)

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# if the first frame is None, initialize it
	if firstFrame is None:
		firstFrame = gray
		continue

	# compute the absolute difference between the current frame and
	# first frame
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
	thresh = cv2.dilate(thresh, None, iterations=2)
	(_, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


	# loop over the contours





	# draw the text and timestamp on the frame
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	cv2.imshow("Bus Finder Feed", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

	#firstFrame = gray


# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
