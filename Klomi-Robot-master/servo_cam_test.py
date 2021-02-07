#!/usr/bin/env python3
"""
Simple test script that moves a servo back and forth while recording video
"""
import RPi.GPIO as GPIO
import time
import sys
from picamera import PiCamera
import os
import numpy as np

camera = PiCamera()
#camera.vflip = True
tiltPin = int(sys.argv[1])
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(tiltPin,GPIO.OUT)
tilt = GPIO.PWM(tiltPin,50.0)
tilt.start(0)
time.sleep(5)
camera.start_recording('/run/menominee/tilt.h264')
step = 0.0025
sleep = step/10.
ZERO = 4 
ONE_EIGHTY = 11
try:
    while True:
        for i in np.arange(ZERO,ONE_EIGHTY,step):
            tilt.ChangeDutyCycle(i)
            time.sleep(sleep)
        for i in np.arange(ONE_EIGHTY,ZERO,-step):
            tilt.ChangeDutyCycle(i)
            time.sleep(sleep)
except KeyboardInterrupt:
    pass
tilt.stop()
GPIO.cleanup()
camera.stop_recording()
#os.system('ffmpeg -framerate 24 -i /run/menominee/tilt.h264 -c copy /tmp/tilt.mp4')
