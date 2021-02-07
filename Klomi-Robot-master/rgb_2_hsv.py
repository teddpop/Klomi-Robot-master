# credit to henrydangprg
import sys
import numpy as np
import cv2

rgb = sys.argv[1]
red = int(rgb[:2],16)
green = int(rgb[2:4],16)
blue = int(rgb[4:],16)
color = np.uint8([[[red, green, blue]]])
hsv_color = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)

hue = hsv_color[0][0][0]
print("lower_bound = [{}, 100, 100]".format(hue-10))
print("upper_bound = [{}, 255, 255]".format(hue+10))
