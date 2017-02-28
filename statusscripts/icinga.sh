#!/bin/bash
#wgets a page on the icinga server
#outputs binary status host/services
#TODO : php page upload 
modepath=/home/pi/naikbled/statusscripts/mode
while true; do
if [[ "$(cat $modepath)" == "1" ]] ; then
    dim=10
    wget -q http://icinga2.mgt.rad.lan/led2.php -O /tmp/icinga.status
    cat /tmp/icinga.status
    host=green
    service=green
    str="/tmp/icinga.status"
    if [[ "$(cat $str | cut -c1)" == "1" ]] ; then host=orange ; fi
    if [[ "$(cat $str | cut -c2)" == "1" ]] ; then host=red ; fi
    if [[ "$(cat $str | cut -c4)" == "1" ]] ; then service=orange ; fi
    if [[ "$(cat $str | cut -c3)" == "1" ]] ; then service=red ; fi
    for f in $(seq  0 9) ; do
        echo "$host,$dim" > /led/led00$f
    done
    for f in $(seq -w 10 19) ; do
        echo "$service,$dim" > /led/led0$f
    done
    sleep 5
fi
done
