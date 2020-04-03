import abc
import cv2
import datetime

class WebcamStream():
    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH )
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT )

    def getWidth(self):
        return self.width 
    
    def getHeight(self):
        return self.height

    def read(self):
        return self.capture.read()


class FPS:
    def __init__(self):
        # store the start time, end time and total number
        # of frames that were examined between start and end
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self
    
    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        return (self._end - self._start).total_seconds()
    
    def fps(self):
        return self._numFrames / self.elapsed()





