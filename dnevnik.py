# -*- coding: utf-8 -*-

from time import sleep, localtime, strftime
import sys
import json
import platform
import smtplib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.select import Select
from ConfigParser import SafeConfigParser
import os.path


CONF_FILE = 'user.conf'
CODING = sys.stdout.encoding

config = SafeConfigParser()
config.read(CONF_FILE)
mosUser = config.get('auth', 'user')
mosPassword = config.get('auth', 'password')
emailUser = config.get('email', 'user')
emailPassword = config.get('email', 'password')
SENDER = config.get('email', 'sender')
SUBJ = config.get('email', 'subject')
RECIPIENT = config.items('email', 'recipients')
URL = config.get('diary', 'url')
DATA_FILE = config.get('diary', 'data_file')

# OS = platform.system()
# isLinux = (OS == 'Linux')
# isWindows = (OS == 'Windows')


def format_time_dmY(func):
    def format():
        return func().strftime("%d.%m.%Y")
    return format


def write_soup_to_file(soup):
    with open(DATA_FILE, 'w') as f:
        f.write(soup.encode('utf-8'))


def read_soup_from_file():
    with open(DATA_FILE) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    return soup


def read_json_from_file():
    with open(DATA_FILE) as f:
        return json.load(f)


def write_json_to_file(info):
    with open(DATA_FILE, 'w') as f:
        f.write(json.dumps(info))


def send_mail(msg_txt):
    msg = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (SENDER, RECIPIENT, SUBJ, msg_txt)
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(emailUser, emailPassword)
        server.sendmail(SENDER, RECIPIENT, msg)
        print '[+] Email successfully sent'
    except:
        print "[-] Error sending email"
    server.quit()


def render_page():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.get(URL)
    driver.find_element_by_name("j_username").send_keys(mosUser)
    driver.find_element_by_name("j_password").send_keys(mosPassword)
    sleep(3)
    driver.find_element_by_id('outerlogin_button').click()
    sleep(10)
    driver.find_element_by_id("button_next").click()
    sleep(7)
    week = driver.find_element_by_class_name("b-diary-st__body")
    return (driver, week.get_attribute('innerHTML'))


def render_next_week():
    driver = render_page()
    nextMonday = get_next_Monday_dmY()
    select = driver.find_element_by_name("next")
    for i in select.find_elements_by_tag_name('option'):
        if i.text == nextMonday:
            i.click()
            sleep(3)
            return driver


def get_Monday():
    now = datetime.now()
    curWeekday = now.weekday()
    return now - timedelta(curWeekday)


@format_time_dmY
def get_Monday_dmY():
    return get_Monday()


def get_next_Monday():
    return get_Monday() + timedelta(7)


@format_time_dmY
def get_next_Monday_dmY():
    return get_Monday() + timedelta(7)


def get_day(tag, day):
    divs = tag.find_all('div', class_='b-diary-week__column')
    for div in divs:
        tmp = div.find('span', class_='b-diary-date')
        date = tmp.get_text().encode('utf-8')
        if date == day:
            return [l for l in div.find_all('div', class_='b-dl-table__list') if l.contents[3].span.string]
    else:
        print 'Ooops! Block with date %s not found' % day
        return False


def get_next_day(tag):
    today = datetime.now()
    weekDay = today.weekday()
    nextDay = (today + timedelta(1)).strftime('%d.%m')
    if weekDay == 6:
        get_next_week()
        print 'Next Week method is not implemented yet'
    else:
        get_day(tag, nextDay)


def get_next_week():
    render_next_week()
    pass


def get_lines(tag):
# res = [l for l in tag.find_all('div', class_='b-dl-table__list') if l.contents[3].span.string]
    res = []
    lines = tag.find_all('div', class_='b-dl-table__list')
    for line in lines:
        if line.contents[3].span.string:
            res.append(line)
    return res


def print_day(day, lines):
    pattern = 'Иностранный'.decode('utf-8')
    print '\n', day
    data_list = []
    for line in lines:
        columns = line.find_all('div', class_='b-dl-td_column')
        tmp = []
        for col in columns:
            txt = col.find('span').text
            if pattern in txt:
                txt = 'Немецкий язык'.decode('utf-8')
            tmp.append(txt.encode(CODING))
        print "{num:3} {subj:35} {grade:8} {task:65} {comment:20}".format(num=tmp[0], subj=tmp[1], task=tmp[2], grade=tmp[3], comment=tmp[4])
        data_list.append(tmp)
    return data_list


def print_day_nextday():
    drv = render_page()
    write_soup_to_file(drv)
    soup = read_soup_from_file()
    today = datetime.now()
    day = today.strftime("%d.%m")
    lines = get_day(soup, day)
    print_day(day, lines)
    nextDay = (today + timedelta(1)).strftime("%d.%m")
    lines = get_day(soup, nextDay)
    print_day(nextDay, lines)
    drv.quit()


def day_to_dict(week, day):
    day_schedule = get_day(week, day)
    data_list = []
    for line in day_schedule:
        columns = line.find_all('div', class_='b-dl-td_column')
        tmp = []
        d = {}
        for col in columns:
            txt = col.find('span').text
            tmp.append(txt)
        d['num'], d['subj'], d['task'], d['grade'], d['comment'] = tmp
        data_list.append(d)
    return data_list


def check_day_grades(list_cur, list_prev):
    diffs = []
    for i in range(len(list_cur)):
        subj = list_cur[i]['subj']
        grade_cur = list_cur[i]['grade']
        grade_prev = list_prev[i]['grade']
        if grade_cur != grade_prev:
            diffs.append((subj, grade_cur))
    return diffs


def create_msg_from_diff(diffs):
    msg = "\nI have got a new grade"
    for diff in diffs:
        subj = diff[0]
        grade = diff[1]
        msg += "%s\t:  %s\n" % (subj, grade)
    return msg


if __name__ == '__main__':
    drv, html_current = render_page()
    day = strftime("%d-%m", localtime())
    soup_current = BeautifulSoup(html_current, 'html.parser')
    info_current = day_to_dict(soup_current, day)

    if not os.path.isfile(DATA_FILE):
        print 'File was absent - no previous info'
        print 'Creating a new week file..........'
        write_soup_to_file(soup_current)
    soup_prev = read_soup_from_file()
    info_prev = day_to_dict(soup_prev, day)

    diff = check_day_grades(info_current, info_prev)
    print 'diff =', diff
    if diff:
        msg = create_msg_from_diff(diff)
        send_mail(msg)

