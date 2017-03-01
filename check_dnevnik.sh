#!/bin/bash

export DISPLAY=:99
/etc/init.d/xvfb start
/usr/bin/python /home/dimka/mos.ru/dnevnik.py >> /home/dimka/mos.ru/dnevnik.log
/etc/init.d/xvfb stop

