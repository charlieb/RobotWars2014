#!/usr/bin/env python
#-------------------------------------------------------------------------------
# track_detect.py
#
# Detects the track by doing the following tasks
# ----------------------------------------------
# 1. Scale the video input and convert to black and white
# 2. Threshold it
# 3. Find contours
# 4. Chose the largest contour and bound it with an elipse or rotated rectangle
# 5. Creating an offset angle from the point in front of the bot to the farthest 
#    point of the bounding primative. This is your tracking error.
#
# + Missing contour will return same error as last time.
# + Set capture_data to True to capture log.avi file to gain insight
#-------------------------------------------------------------------------------
# Written by Scott E. Sindorf
# Copyright 2014, Fluffy White Unicorns
#-------------------------------------------------------------------------------
import numpy as np
import cv2
import cv
#from drivers.config import ConfigFile

class TrackDetect:
    def __init__(self, width, height, source, threshold):
        self.width = width
        self.height = height
        self.threshold = threshold
        self.fourcc = cv.CV_FOURCC('M','J','P','G')
        self.capture_data = False
        
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
        
        self.fx = width / 320.0
        self.fy = height / 240.0
        
        self.heading = 0.0

        if self.capture_data:
            self.writer = cv2.VideoWriter('log.avi', self.fourcc, 6, (self.width, self.height))

    def get_contour(self, img):                
        cnt = None
        ret = False
        contours,_ = cv2.findContours(img, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        num_cnts = len(contours)
        if num_cnts > 0:
            if num_cnts > 1:
                area = 0
                for i in contours:
                    tmp_area = cv2.contourArea(i) 
                    if tmp_area > area:
                        cnt = i
                        area = tmp_area
                if area > 0:
                    ret = True
            else:
                cnt = contours[0]
                ret = True
        if ret == False:
            print 'ERROR! No contours found!'
        return ret, cnt

    def get_heading(self):
        if self.cap.isOpened() == True:
            ret, src_img = self.cap.read()

            if ret == True:
                #cv2.imshow('Source', src_img)	
                sml_img = cv2.resize(src_img, (0,0), fx=self.fx, fy=self.fy)

                dy = 0
                bw_img = cv2.cvtColor(sml_img, cv.CV_RGB2GRAY)
                #cv2.imshow('Black & White', bw_img)	
                _, thresh_img = cv2.threshold(bw_img, self.threshold, 255, cv2.THRESH_BINARY_INV)
                #cv2.imshow('Threshold', thresh_img)	
                
                ret, cnt = self.get_contour(thresh_img)
                if ret == True:
                    if len(cnt) >= 5:
                        ellipse = cv2.fitEllipse(cnt)
                        if self.capture_data:
                            cv2.ellipse(sml_img, ellipse, (0,255,255), 2)
                        box = cv.BoxPoints(ellipse)
                        box = np.int0(box)
                    else:
                        rect = cv2.minAreaRect(cnt)
                        box = cv.BoxPoints(rect)
                        box = np.int0(box)
                        if self.capture_data:
                            cv2.drawContours(sml_img,[box],0,(255,255, 0),2)

                    box = box[box[:,1].argsort()]
                    p0 = ((box[0][0]+box[1][0])/ 2, (box[0][1]+box[1][1])/ 2)
                    p1 = (self.width/2, self.height-1)
                    dx = p1[0]-p0[0]
                    dy = p1[1]-p0[1]
                    
                    if self.capture_data:
                        cv2.line(sml_img, p0, p1, (0,0,255), 2)
                        self.writer.write(sml_img)

                    if dy != 0:
                        self.heading = np.arctan(float(dx)/dy)
                    
                return (True, self.heading)
        return (False, 0)

    def __del__(self):
        self.cap.release()
        
