#!/bin/bash
PORT=6681
mpc -p $PORT insert "file:$1"
