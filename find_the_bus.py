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
delay_feed = False

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
	#frame = imutils.resize(frame, width=500)

	if args.get("video", None) is None:
		crop_img = frame[100:200, 250:350]
	else:
		crop_img = frame[50:150, 150:300]

	frame = crop_img
	frame = imutils.resize(frame, width=500)

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
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < args["min_area"]:
			continue


		path = "captures/{timestamp}.png".format(timestamp=ts).replace(' ', '')
		cv2.imwrite(path, frame)
		f = open(path, 'r+')

		rows = open('models/synset_words_edit.txt').read().strip().split("\n")
		classes = [r[r.find(" ") + 1:].split(",")[0] for r in rows]

		blob = cv2.dnn.blobFromImage(frame, 1, (224, 224), (104, 117, 123))

		net = cv2.dnn.readNetFromCaffe('models/bvlc_googlenet.prototxt', 'models/bvlc_googlenet.caffemodel')

		net.setInput(blob)
		start = time.time()
		preds = net.forward()
		end = time.time()
		print("[INFO] classification took {:.5} seconds".format(end - start))

		# sort the indexes of the probabilities in descending order (higher
		# probabilitiy first) and grab the top-5 predictions
		idxs = np.argsort(preds[0])[::-1][:5]

		# loop over the top-5 predictions and display them
		for (i, idx) in enumerate(idxs):
			# draw the top prediction on the input image
			if (i == 0 and  preds[0][idx] > 0. and classes[idx] == 'school bus' and not delay_feed) :
				text = "Label: {}, {:.2f}%".format(classes[idx],
					preds[0][idx] * 100)
				cv2.putText(frame, text, (5, 25),  cv2.FONT_HERSHEY_SIMPLEX,
					0.7, (0, 0, 255), 2)
				# display the output image
				cv2.imshow("Image", frame)

				s3.upload_fileobj( f, 'xs-schoolbus', path, ExtraArgs={'ACL': 'public-read'})
				url = "https://s3.amazonaws.com/xs-schoolbus/"+path

				sc.api_call(
				  "chat.postMessage",
				  channel="#schoolbus",
				  text= "THE BUS IS COMING!!:tada: "+url
				)

				delay_feed = True


			# display the predicted label + associated probability to the
			# console
			print("[INFO] {}. label: {}, probability: {:.5}".format(i + 1,
				classes[idx], preds[0][idx]))




	# draw the text and timestamp on the frame
	cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame and record if the user presses a key
	#cv2.imshow("Original", firstFrame)
	cv2.imshow("Bus Finder Feed", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

	firstFrame = gray

	if delay_feed:
		time.sleep(2.00)
		delay_feed = False

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
