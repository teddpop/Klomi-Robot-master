# mask the test image
import numpy as np
import cv2
import sys
def rgb2hsv(rgb):
    red = int(rgb[:2],16)
    green = int(rgb[2:4],16)
    blue = int(rgb[4:],16)
    color = np.uint8([[[red, green, blue]]])
    hsv_color = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
    hue = hsv_color[0][0][0]
    lower = np.array([hue - 10, 100, 100],dtype='uint8')
    upper = np.array([hue + 10, 255, 255],dtype='uint8')
    return lower, upper

lower, upper = rgb2hsv(sys.argv[1])

img = cv2.imread(sys.argv[2],1)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv,lower,upper)
cv2.imshow('mask',mask)
cv2.imshow('image',img)

while 1:
    k = cv2.waitKey(0)
    if(k == 27):
        break

cv2.destroyAllWindows()
