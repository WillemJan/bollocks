#!/bin/bash
#sets random lichts when mode is 2
#TODO .. number of leds from config file
modepath=/home/pi/naikbled/statusscripts/mode
while true; do
if [[ "$(cat $modepath)" == "2" ]] ; then

        for f in $(seq -w 0 31); do
                color=$(cat ../pygame_colormap.json  | grep ":" | cut -f2 -d\" | head  -$(echo $RANDOM % 656 + 1 | bc ) | tail -1)
                echo $color,2 > /led/led0$f 
        done
        sleep 5
fi
done
