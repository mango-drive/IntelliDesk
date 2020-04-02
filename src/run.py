import argparse
import datetime
import time

import cv2
import imutils
from imutils.video import VideoStream
from pyzbar import pyzbar

# from workstation import Logger, WorkStation

time.sleep(1.0)

width = vs.get(cv2.CAP_PROP_FRAME_WIDTH )
height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT )
fps =  vs.get(cv2.CAP_PROP_FPS)

# Check if camera opened successfully
if (vs.isOpened()== False): 
  print("Error opening video stream or file")
      
workstation = WorkStation(width, height)
artist = Artist()
logger = Logger()
csv = open("barcodes.csv", "w")
found = set()

while True:
    # Read the frame from the video capture
    ret, frame = vs.read()
    # artist.draw_workstation(frame, workstation) 
    # Get all barcodes within the frame
    barcodes = pyzbar.decode(frame)
    artist.draw_barcodes(frame, barcodes)
    # Locate the barcodes within the workstation's areas
    # task = workstation.process(barcodes)

    # logger.log(task)
          # 
    # Display the frame
    cv2.imshow("Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

