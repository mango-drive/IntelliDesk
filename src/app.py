#!/usr/bin/env python
import argparse
import datetime
import time
import os

import cv2
import imutils
from flask import Flask, Response, render_template, jsonify
from flask_cors import CORS
from imutils.video import VideoStream
from pyzbar import pyzbar

from workstation import Artist, WorkStation

useTestingVideo = True
usePiCamera = False

if not useTestingVideo:
    try:
        from picamera import picamera
        usePiCamera = True
    except:
        usePiCamera = False

if useTestingVideo:
    vs = cv2.VideoCapture('../vid/test.mp4')
    if (vs.isOpened() == False):
        print("Error opening video stream file")
    else:
        width = vs.get(cv2.CAP_PROP_FRAME_WIDTH )
        height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT )

elif usePiCamera:
    vs = VideoStream(src=0, usePicamera=usePiCamera).start()
    (width, height) = vs.stream.camera.resolution
else:
    vs = cv2.VideoCapture(0)
    width = vs.get(cv2.CAP_PROP_FRAME_WIDTH )
    height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT )

app = Flask(__name__) 
CORS(app)
app._static_folder = os.path.abspath("templates/static/")
time.sleep(1.0)

workstation = WorkStation(width, height)
artist = Artist()

task = {"mode": "test", "base": "test", "from": "test", "work": "test", "save": "test"}

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def stream_is_open():
    if useTestingVideo:
        return vs.isOpened()
    else:
        # return true for cameras
        return True

def development_gen():
    while stream_is_open():
        rval, frame = vs.read()
        barcodes = pyzbar.decode(frame)
        global task
        task = workstation.process(barcodes)

        artist.draw_workstation(workstation, frame)

        # cv2.imshow('test_video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def gen():
    """Video streaming generator function."""
    while stream_is_open():
        rval, frame = vs.read()

        barcodes = pyzbar.decode(frame)
        global task
        task = workstation.process(barcodes)

        artist.draw_workstation(workstation, frame)
        cv2.imwrite('t.jpg', frame)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/long_poll')
def long_poll():
    global task
    if task:
        update = jsonify(task)
        return update
    else:
        return jsonify("nothing")
    
if __name__ == '__main__':
    port = 80 if usePiCamera else 5000
    # development_gen()
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
