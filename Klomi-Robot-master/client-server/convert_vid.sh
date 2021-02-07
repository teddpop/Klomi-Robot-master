#!/bin/bash
rm -f tmp.mp4
ffmpeg -f mjpeg -i <(curl http://10.42.0.81:8000/stream.mjpg) -f mp4 tmp.mp4
