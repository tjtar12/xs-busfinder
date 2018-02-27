# import the necessary packages
import numpy as np
import argparse
import cv2
from matplotlib import pyplot as plt

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help = "path to the image")
args = vars(ap.parse_args())

# load the image
image = cv2.imread(args["image"])

# define the list of boundaries BGR
boundaries = [
	([100,180,245], [120,210,255])
#([160,245,100], [170,255,120])
]

# loop over the boundaries
for (lower, upper) in boundaries:
	# create NumPy arrays from the boundaries
	lower = np.array(lower, dtype = "uint8")
	upper = np.array(upper, dtype = "uint8")

	# find the colors within the specified boundaries and apply
	# the mask
	mask = cv2.inRange(image, lower, upper)
	output = cv2.bitwise_and(image, image, mask = mask)

	# img = cv2.imread('home.jpg')
	color = ('b','g','r')
	for i,col in enumerate(color):
	    histr = cv2.calcHist([image],[i],None,[256],[0,256])
	    plt.plot(histr,color = col)
	    plt.xlim([0,256])
	plt.show()


	# show the images
	cv2.imshow("images", np.hstack([image, output]))
	cv2.waitKey(0)
