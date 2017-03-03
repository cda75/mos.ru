import smtplib
import json
import platform
from bs4 import BeautifulSoup
from time import strftime, localtime


# Decorators for nice printing
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


# File operaitions
def read_json_from_file(fName):
    with open(fName) as f:
        return json.load(f)


def write_json_to_file(fName, info):
    with open(fName, 'w') as f:
        f.write(json.dumps(info))


def write_soup_to_file(fName, soup):
    with open(fName, 'w') as f:
        f.write(soup.encode('utf-8'))


def read_soup_from_file(fName):
    with open(fName) as f:
        return BeautifulSoup(f.read(), 'html.parser')


# E-mail sender
def send_mail(header, msg_txt):
    eUser, ePassword, send, recip, subj = header
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (send, recip, subj, msg_txt)
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(eUser, ePassword)
        server.sendmail(send, recip, msg)
        print '[+] Email successfully sent'
    except:
        print "[-] Error sending email"
    finally:
        server.quit()


def get_OS():
    return platform.system()
