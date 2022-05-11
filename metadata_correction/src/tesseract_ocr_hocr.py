# USAGE
# python tesseract.py --image images/paper-01.tif 
# python tesseract.py --image images/paper-02.tif  --preprocess blur

# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os

# If you don't have tesseract executable in your PATH, include the following:
#pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
	help="type of preprocessing to be done")
ap.add_argument("-t", "--txt", required=True,
	help="path to output text file after OCR")
ap.add_argument("-o", "--hOCR", required=True,
	help="path to output hOCR file after OCR")
args = vars(ap.parse_args())

# load the example image and convert it to grayscale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

cv2.imshow("Image", gray)

# check to see if we should apply thresholding to preprocess the
# image
if args["preprocess"] == "thresh":
	gray = cv2.threshold(gray, 0, 255,
		cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# make a check to see if median blurring should be done to remove
# noise
elif args["preprocess"] == "blur":
	gray = cv2.medianBlur(gray, 3)

# write the grayscale image to disk as a temporary file so we can
# apply OCR to it
filename = "{}.tif".format(os.getpid())
cv2.imwrite(filename, gray)

# load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file

text = pytesseract.image_to_string(Image.open(filename)) #Get the text file format output
hocr = pytesseract.image_to_pdf_or_hocr(Image.open(filename), extension='hocr') #Get the hocr file format output
hocr = hocr.decode('utf-8')

os.remove(filename)  

#write the output into new txt and html files
filename_txt = f"txt/{args['txt']}"
filename_html = f"hocr/{args['hOCR']}"

with open(filename_txt, "w") as f:
	f.write(text)

with open(filename_html, "w") as g:
	g.write(hocr)
