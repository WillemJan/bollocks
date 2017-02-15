#!/bin/bash
dim=2
wget http://localhost/cpu.php -O /tmp/cpu.status
load=$(cat /tmp/cpu.status)
if [[ $load > 99 ]] ; then 
    for f in $(seq -w 001 100) ; do
    echo "orange,dim" > /led/led$f
    done
    for f in $(seq -w 100 $load) ; do
    echo "red,dim" > /led/led$f
    done
else
    for f in $(seq -w 001 $load) ; do
    echo "orange,$dim" > /led/led$f
    done
fi
for f in $(seq -w $load 255) ; do
echo "black," > /led/led$f
done


