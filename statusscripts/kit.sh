#!/bin/bash
# quick test ...  why no work??!? 
cd /home/pi/naikbled/statusscripts/
while true; do
if [[ "$(cat mode)" == "5" ]] ; then
    dim=100
    for f in $(seq -w 0 31) ; do
        for g in $(seq -w 0 31) ; do
                if [ $g == $f ] ; then 
                echo "red,$dim" > /led/led0$g 
                else 
                echo "black,$dim" > /led/led0$g
                fi
        done
        sleep 0.5
    done
    for f in $(seq -w 31 0) ; do
        for g in $(seq -w 0 31) ; do
                if [ $g == $f ] ; then 
                echo "red,$dim" > /led/led0$g 
                else 
                echo "black,$dim" > /led/led0$g
                fi
        done
        sleep 0.5
    done
fi
done
