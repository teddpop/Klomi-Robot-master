import os 
import cv2
import numpy as np
import imutils
from imutils.object_detection import non_max_suppression


class ObjectFinder():
    def __init__(self):
        self._frame = None

    def findObject(self,frame):
        self._frame = frame
        return None

    def getMask(self):
        return self._frame


class ColorFinder(ObjectFinder):
    def rgb2hsv(self,rgb):
        red = int(rgb[:2],16)
        green = int(rgb[2:4],16)
        blue = int(rgb[4:],16)
        color = np.uint8([[[red, green, blue]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
        hue = hsv_color[0][0][0]
        lower = np.array([hue - 10, 80, 80],dtype='uint8')
        upper = np.array([hue + 10, 255, 255],dtype='uint8')
        return lower, upper

    def __init__(self,color):
        self.lower, self.upper = self.rgb2hsv(color)

    def findObject(self,frame):
        tiny_frame =imutils.resize(frame, width=200)
        hsv = cv2.cvtColor(tiny_frame, cv2.COLOR_BGR2HSV)
        # mask the object of the color we want
        mask = cv2.inRange(hsv,self.lower,self.upper)
        mask = cv2.erode(mask,None,iterations=2)
        self._frame = cv2.dilate(mask,None,iterations=2)
        
        #find the centroid of the largest contor in the mask
        cnts = cv2.findContours(self._frame.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)[-2]
        if cnts:
            c = max(cnts,key=cv2.contourArea)
            M = cv2.moments(c)
            center = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            cv2.circle(self._frame,center, 5, (0,255,255), 2)
            center = (center[0]/self._frame.shape[0], 
                    center[1]/self._frame.shape[1])
            return center
        else:
            return None

class HOGPersonFinder(ObjectFinder):
    def __init__(self):
        super().__init__()
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def findObject(self,frame):
        frame = imutils.resize(frame, width=400)
     
        # detect people in the image
        (rects, weights) = self.hog.detectMultiScale(frame, winStride=(4, 4),
            padding=(8, 8), scale=1.05)
     
        # apply non-maxima suppression to the bounding boxes using a
        # fairly large overlap threshold to try to maintain overlapping
        # boxes that are still people
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        #pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
     
        self._frame = frame
        # draw the final bounding boxes
        #for (xA, yA, xB, yB) in pick:
        #    cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)
        print("FRAME!!!")
        return None


class ServerFinder(ObjectFinder):
    pass
