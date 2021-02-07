#!/usr/bin/env python3
"""
Simple test script that takes a static picture
"""
from picamera import PiCamera
import os
camera = PiCamera()
camera.vflip = True
camera.capture('/run/menominee/pic.jpg')
os.system('gnome-paint /run/menominee/pic.jpg')
