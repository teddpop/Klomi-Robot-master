#!/usr/bin/env python3
import numpy as np
import cv2
import imutils
import RPi.GPIO as GPIO
import time
import sys
from ObjectFinder import ColorFinder, HOGPersonFinder

TILT_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class Camera():
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.out = cv2.VideoWriter('/run/menominee/out.avi',
                cv2.VideoWriter_fourcc('M','J','P','G'), 
                10, (width,height))

    def frames(self):
        while 1:
            status, frame = self.camera.read()
            if not status:
                raise StopIteration
            self.frame = imutils.rotate(frame,angle=180)
            yield self.frame
            cv2.waitKey(1)

    def write(self):
        self.out.write(self.frame)

    def release(self):
        self.camera.release()
        self.out.release()

class ServoController():
    ZERO = 2
    ONE_EIGHTY = 13
    def __init__(self, pin):
        self.NINETY = (self.ZERO + self.ONE_EIGHTY)/2.
        self.pin = pin
        self.duty_cycle = self.NINETY
        GPIO.setup(self.pin,GPIO.OUT)

    def setCycle(self,duty_cycle):
        if duty_cycle < self.ZERO:
            duty_cycle = self.ZERO
        if duty_cycle > self.ONE_EIGHTY:
            duty_cycle = self.ONE_EIGHTY

        tilt = GPIO.PWM(self.pin,50.0)
        tilt.start(8)
        tilt.ChangeDutyCycle(duty_cycle)
        time.sleep(.001)
        tilt.stop()


    def move_towards(self,point):
        """ Point should be normalized """
        if not point:
            return
        x, y = point
        if x < 1/6:
            self.duty_cycle += .2
            self.setCycle(self.duty_cycle)
        elif x < 1/3:
            self.duty_cycle += .1
            self.setCycle(self.duty_cycle)
        elif x > 2/3:
            self.duty_cycle -= .1
            self.setCycle(self.duty_cycle)
        elif x > 5/6:
            self.duty_cycle -= .2
            self.setCycle(self.duty_cycle)


def main():
    frame_count = 0
    servos = ServoController(TILT_PIN)
    cam = Camera()
    #finder = ColorFinder(sys.argv[1])
    finder = HOGPersonFinder()
    try:
        for frame in cam.frames():
            center = finder.findObject(frame)
            servos.move_towards(center)
            cv2.imshow("frame", finder.getMask())
    except KeyboardInterrupt:
        cam.release()

if __name__ == '__main__':
    main()
    cv2.destroyAllWindows()
