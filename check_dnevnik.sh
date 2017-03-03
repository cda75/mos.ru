#!/bin/bash

export DISPLAY=:99
echo "Start checking diary......"
/etc/init.d/xvfb start
/usr/bin/python /home/dimka/mos.ru/dnevnik.py 
/etc/init.d/xvfb stop
echo "Diary successfully checked"

