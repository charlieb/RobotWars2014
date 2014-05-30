#!/usr/bin/env python
#-------------------------------------------------------------------------------
# track_runner.py
#
# Navigate a black track on a white background
#---------------------------------------------
# + Adjust KP if up if bot drifts off track on straight away
# + Adjust KP down if bot oscillates on straight away
# + Adjust KD up if bot undershoots the turn
# + Adjust KD down if bot overshoots the turn
# + Work with short times until bot behaves properly
# + Changing speeds requires retuning the KP and HD values 
# + Beware of limited battery life
# + Set log_data to True to aquire log.txt file. This data is comma delimited 
#   so import into Excel and graph for some insight.
#-------------------------------------------------------------------------------
# Written by Scott E. Sindorf
# Copyright 2014, Fluffy White Unicorns
#-------------------------------------------------------------------------------
import time
import numpy as np
import cv2
import cv
from drivers.motor import MotorDriver
from drivers.pid import PID
from track_detect import TrackDetect

WIDTH     = 80
HEIGHT    = 60
THRESHOLD = 128
KP        = 400.0
KD        = 10.0
KI        = 0.0
MIN_SPEED = -99
MAX_SPEED = 99
speed     = 40
RUN_TIME  = 30 #seconds
log_data  = False


td  = TrackDetect(WIDTH, HEIGHT, 0, THRESHOLD)
#td  = TrackDetect(WIDTH, HEIGHT, 'pictures/track_160x120.avi', 64)

pid = PID(KP, KD, KI)
motors = MotorDriver(0.0)

ret = True;
if log_data:
    log = open('log.txt', 'w')
    log.write("Heading,Diff/Error\n")

time.sleep(10)


cap_time = time.time()
end_time = cap_time + RUN_TIME

# Limit time while testing so bot doesn't get away from you and log only has important data
while cap_time < end_time:
    ret, heading = td.get_heading()
    if ret:
        # Output of PID is the total track speed differential which is 
        # distributed about the speed setting
        diff = pid.GenOut(heading)
        half_diff = int(diff/2.0)
        left_track = speed - half_diff
        right_track = speed + half_diff
        
        # Offset speed to maximize differential rather than clipping
        offset = 0

        if diff < 0:
            if left_track < MIN_SPEED:
                offset = -left_track
            elif right_track > MAX_SPEED:
                offset = right_track - MAX_SPEED
        else:
            if left_track > MAX_SPEED:
                offset = left_track - MAX_SPEED
            elif right_track < MIN_SPEED:
                offset = -right_track

        new_left_track = left_track - offset
        new_right_track = right_track - offset
        
        if log_data:
            log.write("%s,%s\n" % (np.degrees(heading),  diff))
        
        motors.setSpeed(new_left_track, new_right_track)
        cap_time = time.time()

motors.stopMotors()

if log_data:
    log.close()
