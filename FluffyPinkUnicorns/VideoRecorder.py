import time
import cv2
import cv

WIDTH  = 320
HEIGHT = 240
FRAME_RATE = 6
FRAME_PERIOD = 1.0 / FRAME_RATE
RECORD_TIME = 60 #seconds

cap_time = time.time()
end_time = cap_time + RECORD_TIME
next_frame_time = cap_time

c = cv2.VideoCapture(0)

c.set(cv.CV_CAP_PROP_FRAME_WIDTH, WIDTH)
c.set(cv.CV_CAP_PROP_FRAME_HEIGHT, HEIGHT)

fourcc = cv.CV_FOURCC('M','J','P','G')
w = cv2.VideoWriter('test.avi', fourcc, FRAME_RATE, (WIDTH, HEIGHT))

while cap_time < end_time:
    if cap_time >= next_frame_time:
        w.write(c.read()[1])
        next_frame_time += FRAME_PERIOD
    cap_time = time.time()

