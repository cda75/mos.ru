# -*- coding: utf-8 -*-

import smtplib
import json
import platform
from time import strftime, localtime


def print_line(func):
    def wrapper(*args, **kwargs):
        print '----------------------------------------------'
        return func(*args, **kwargs)
    return wrapper


def add_current_time(func):
    def wrapper(*args, **kwargs):
        print strftime("%d.%m.%Y %H:%M", localtime())
        return func(*args, **kwargs)
    return wrapper


def read_json_from_file(fName):
    with open(fName) as f:
        return json.load(f)


def write_json_to_file(fName, info):
    with open(fName, 'w') as f:
        f.write(json.dumps(info))


def send_mail(emailUser, emailPassword, sender, recipient, subj, msg_txt):
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (sender, recipient, subj, msg_txt)
    print 'email msg:\n', msg
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(emailUser, emailPassword)
        server.sendmail(sender, recipient, msg)
        print '[+] Email successfully sent'
    except:
        print "[-] Error sending email"
    finally:
        server.quit()


def get_OS():
    return platform.system()
