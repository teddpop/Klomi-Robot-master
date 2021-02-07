#!/bin/bash
# run this one once at startup to add camera drivers
sudo sh << EOF
mkdir -p /run/menominee
modprobe bcm2835-v4l2
chown pi /run/menominee/
pigpiod
pkill mpd
EOF
vncserver
