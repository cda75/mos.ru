#!/bin/bash

export DISPLAY=:99
/etc/init.d/xvfb start
/usr/bin/python /home/dimka/mos.ru/sad.py >> sad.log 
/etc/init.d/xvfb stop

