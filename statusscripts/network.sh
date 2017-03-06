#!/bin/bash
while true; do
if [[ "$(cat /home/pi/naikbled/statusscripts/mode)" == "2" ]] ; then
SUBNET=$(cat /home/pi/naikbled/statusscripts/subnet)
NUMLEDS=27 # this needs to be placed in a config file
seq 1 $NUMLEDS | while read ; do echo $SUBNET.$REPLY ;done  |  xargs -P 10 -n1 ping -c 1 -w 1 -i 0.2 -n -q | grep -B1 "0% packet" > /tmp/net
cat /tmp/net  | grep -B1 " 0%" | grep statis  | cut -f4 -d. | cut -f1 -d" " | while read ;do led=$(printf "%03d" $REPLY) ; echo  "green,50" > /led/led$led ;done
cat /tmp/net  | grep -B1 100% | grep statis  | cut -f4 -d. | cut -f1 -d" " | while read ;do led=$(printf "%03d" $REPLY) ; echo  "red,50" > /led/led$led ;done
fi
done

