# -*- coding: utf-8 -*-

from helper import TimeTable
from argparse import ArgumentParser


# mosURL = config.get('diary', 'url')
# emailUser = config.get('email', 'user')
# emailPassword = config.get('email', 'password')
# SENDER = config.get('email', 'sender')
# SUBJ = config.get('email', 'subject')
# RECIPIENT = config.get('email', 'recipients')
# mail_header = (emailUser, emailPassword, SENDER, RECIPIENT, SUBJ)
# DATA_FILE = config.get('diary', 'data_file')


parser = ArgumentParser(description='CLI for Electronic Diary at mos.ru')
parser.add_argument("-action", type=str, dest='action', default='print', help='Type of action: check or print')
parser.add_argument("-date", type=str, dest='date', default='today', help='Time-day for action: dd.mm format')
args = parser.parse_args()
action = args.action
day = args.date

T = TimeTable()
T.main(action, day)
