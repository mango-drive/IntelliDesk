#!/usr/bin/env python
import argparse
import datetime
import time

import cv2
import imutils
from flask import Flask, Response, render_template
from flask_cors import CORS
from imutils.video import VideoStream
from pyzbar import pyzbar

from workstation import Artist, Logger, WorkStation

try:
  from picamera import picamera
  usePiCamera = True
except:
  usePiCamera = False

if usePiCamera:
    vs = VideoStream(src=0, usePicamera=usePiCamera).start()
    (width, height) = vs.stream.camera.resolution
else:
    vs = cv2.VideoCapture(0)
    width = vs.get(cv2.CAP_PROP_FRAME_WIDTH )
    height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT )

app = Flask(__name__) 
CORS(app)
time.sleep(1.0)

workstation = WorkStation(width, height)
artist = Artist()
logger = Logger()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    """Video streaming generator function."""
    while True:
        rval, frame = vs.read()

        barcodes = pyzbar.decode(frame)
        task = workstation.process(barcodes)
        logger.log(task)

        artist.draw_workstation(frame, workstation)
        cv2.imwrite('t.jpg', frame)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = 80 if usePiCamera else 5000
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
