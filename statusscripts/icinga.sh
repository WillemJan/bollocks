#!/bin/bash
while true; do
if [[ "$(cat mode)" == "1" ]] ; then
    dim=10
    wget -q http://localhost/icinga.php -O /tmp/icinga.status
    cat /tmp/icinga.status
    host=green
    service=green
    str="/tmp/icinga.status"
    if [[ "$(cat $str | cut -c1)" == "1" ]] ; then host=orange ; fi
    if [[ "$(cat $str | cut -c2)" == "1" ]] ; then host=red ; fi
    if [[ "$(cat $str | cut -c3)" == "1" ]] ; then service=orange ; fi
    if [[ "$(cat $str | cut -c4)" == "1" ]] ; then service=red ; fi
    for f in $(seq -w 1 10) ; do
	echo "$host,$dim" > /led/led0$f
    done
    for f in $(seq -w 11 20) ; do
	echo "$service,$dim" > /led/led0$f
    done
    sleep 5
fi
done
