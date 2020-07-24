from __future__ import print_function
import cv2 
import argparse
from numpy import *
from config import DETECT_NUM


def detectAndDisplay(frame, face_cascade):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ##resized = cv2.resize(frame_gray,None,fx,fx,cv2.INTER_AREA)
    ##frame_gray = cv2.equalizeHist(frame_gray)
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray,1.3,DETECT_NUM)

    return faces
