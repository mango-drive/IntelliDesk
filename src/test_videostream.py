from videostream import FPS, WebcamVideoStream
import cv2
import imutils

# print("[INFO] sampling frames from webcam...")
# stream = cv2.VideoCapture(0)
# fps = FPS().start()

# while fps._numFrames < 100:
#     (grabbed, frame) = stream.read()
#     fps.update()

# fps.stop()
# print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# stream.release()


print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()

while fps._numFrames < 100:
    frame = vs.read()
    fps.update()

fps = FPS().stop()