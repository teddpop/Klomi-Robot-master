#!/bin/bash
source ../useful_vars
#python real_time_object_detection.py -p $PROTOTXT -m $MODEL -s $PI -v &
python process_stream.py $PI
