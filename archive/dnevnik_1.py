# -*- coding: utf-8 -*-

from helper import TimeTable
from argparse import ArgumentParser



parser = ArgumentParser(description='CLI for Electronic Diary at mos.ru')
parser.add_argument("-action", type=str, dest='action', default='print', help='Type of action: check or print')
parser.add_argument("-date", type=str, dest='date', default='today', help='Time-day for action: dd.mm format')
args = parser.parse_args()
action = args.action
day = args.date

T = TimeTable()
T.main(action, day)
