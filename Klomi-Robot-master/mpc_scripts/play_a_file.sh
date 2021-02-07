#!/bin/bash
PORT=6681

mpc -p $PORT clear
mpc -p $PORT add "file:$1"
mpc -p $PORT play
while [[ ! -z `mpc -p $PORT current` ]]; do sleep 0.1; done
mpc -p $PORT clear
