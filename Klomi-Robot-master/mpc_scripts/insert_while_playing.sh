#!/bin/bash
PORT=6681
PAUSE_TIME=`mpc -p $PORT pause | grep -o "[0-9]\+:[0-9]\+" | head -1`
mpc -p $PORT insert "file:$1"
mpc -p $PORT next
while [[ $1 = `mpc -p $PORT current` ]]; do sleep 0.1; done
