# -*- coding: utf-8 -*-

from helper import TimeTable
from ConfigParser import SafeConfigParser


CONF_FILE = 'user.conf'
config = SafeConfigParser()
config.read(CONF_FILE)

mosURL = config.get('diary', 'url')
mosUser = config.get('auth', 'user')
mosPassword = config.get('auth', 'password')

emailUser = config.get('email', 'user')
emailPassword = config.get('email', 'password')
SENDER = config.get('email', 'sender')
SUBJ = config.get('email', 'subject')
RECIPIENT = config.get('email', 'recipients')
mail_header = (emailUser, emailPassword, SENDER, RECIPIENT, SUBJ)

DATA_FILE = config.get('diary', 'data_file')


if __name__ == '__main__':
    T = TimeTable(user=mosUser, password=mosPassword)
    T.print_day('next')



