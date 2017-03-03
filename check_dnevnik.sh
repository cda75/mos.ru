#!/bin/bash

export DISPLAY=:99
/etc/init.d/xvfb start
echo "Xvfb started at DISPLAY 99"
echo "Start checking diary......"
/usr/bin/python /home/dimka/mos.ru/dnevnik.py 
/etc/init.d/xvfb stop
echo "Diary successfully checked"

