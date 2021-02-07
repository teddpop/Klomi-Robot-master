#!/bin/bash
PORT=6681
MY_DIR=`dirname "$0"`
# get a list of songs and select a random one
SONGS=`mpc -p $PORT search any "$1" | shuf | head -5`
echo $SONGS
$MY_DIR/mpc_scripts/play_a_file.sh /home/pi/goog/quack.mp3
while read -r song; do
	mpc -p $PORT add "$song"
done <<< "$SONGS"
mpc -p $PORT play
