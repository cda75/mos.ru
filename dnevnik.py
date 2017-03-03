# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from ConfigParser import SafeConfigParser
import os.path
import helper


CONF_FILE = 'user.conf'
CODING = sys.stdout.encoding

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


def format_time_dmY(func):
    def format():
        return func().strftime("%d.%m.%Y")
    return format


def format_time_dm(func):
    def format():
        return func().strftime("%d.%m")
    return format


def render_page():
    driver = webdriver.Firefox()
    driver.get(mosURL)
    wait = WebDriverWait(driver, 15)
    elem1 = "//a[@class='chosen-single']/span[.='K1617']"
    elem2 = "//div[@class='b-diary-st__body']"
    driver.find_element_by_name("j_username").send_keys(mosUser)
    driver.find_element_by_name("j_password").send_keys(mosPassword)
    driver.find_element_by_id('outerlogin_button').click()
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, elem1)))
        driver.find_element_by_id("button_next").click()
        diary = wait.until(EC.presence_of_element_located((By.XPATH, elem2)))
        html = diary.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        return (driver, soup)
    except NoSuchElementException:
        print "Ooops! Element was not found probably because of timing issue"


def render_next_week():
    driver = render_page()
    nextMonday = get_next_Monday_dmY()
    select = driver.find_element_by_name("next")
    for i in select.find_elements_by_tag_name('option'):
        if i.text == nextMonday:
            i.click()
#            sleep(3)
            return driver


@format_time_dm
def get_current_day():
    today = datetime.now()
    return today


@format_time_dm
def get_next_day():
    today = datetime.now()
    nextDay = today + timedelta(1)
    return nextDay


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


def get_day(soup, day):
    divs = soup.find_all('div', class_='b-diary-week__column')
    for div in divs:
        tmp = div.find('span', class_='b-diary-date')
        date = tmp.get_text().encode('utf-8')
        if date == day:
            return get_lines(div)
    else:
        print 'Ooops! Block with date %s not found' % day


def get_lines(tag):
    res = []
    lines = tag.find_all('div', class_='b-dl-table__list')
    for line in lines:
        if line.contents[3].span.string:
            res.append(line)
    return res


def print_day(lines):
    pattern = 'Иностранный'.decode('utf-8')
    data_list = []
    for line in lines:
        columns = line.find_all('div', class_='b-dl-td_column')
        tmp = []
        for col in columns:
            txt = col.find('span').text
            if pattern in txt:
                txt = 'Немецкий язык'.decode('utf-8')
            tmp.append(txt.encode(CODING))
        print "{num:3} {subj:32} {grade:6} {task:65} {comment:15}".format(num=tmp[0], subj=tmp[1], task=tmp[2], grade=tmp[3], comment=tmp[4])
        data_list.append(tmp)
    return data_list


def print_day_nextday(soup):
    days = [get_current_day(), get_next_day()]
    for day in days:
        lines = get_day(soup, day)
        print_day(lines)


def day_to_dict(soup, day):
    lines = get_day(soup, day)
    data_list = []
    for line in lines:
        columns = line.find_all('div', class_='b-dl-td_column')
        tmp = []
        d = {}
        for col in columns:
            txt = col.find('span').text
            tmp.append(txt)
        d['num'], d['subj'], d['task'], d['grade'], d['comment'] = tmp
        data_list.append(d)
    return data_list


def compare_grades(list_cur, list_prev):
    diffs = []
    for i in range(len(list_cur)):
        subj = list_cur[i]['subj']
        grade_cur = list_cur[i]['grade']
        grade_prev = list_prev[i]['grade']
        if grade_cur != grade_prev:
            diffs.append((subj, grade_cur))
    return diffs


@helper.print_line
@helper.add_current_time
def send_alert(diffs):
    msg = "\n"
    for diff in diffs:
        msg += "%s\t\t%s\n" % (diff[0], diff[1])
    print "Sending e-mail .........."
    helper.send_mail(mail_header, msg.encode('utf-8'))
    return True


@helper.print_line
@helper.add_current_time
def nothing_New(day, soup):
    print 'No new grades\n'
    lines = get_day(soup, day)
    print_day(lines)


def check_day(day, soup_current):
    # Get info from html variable
    info_current = day_to_dict(soup_current, day)

    # Check if data_file exist. If not - create it and print current info
    if not os.path.isfile(DATA_FILE):
        print 'File was absent - no previous info'
        print 'Creating a new week file..........'
        helper.write_soup_to_file(DATA_FILE, soup_current)
        return False

    # Read info from previous try
    soup_prev = helper.read_soup_from_file(DATA_FILE)
    info_prev = day_to_dict(soup_prev, day)

    # Cheking If something were added to the current Schedule
    if len(info_current) > len(info_prev):
        print "New lessons were added from the last time"
        info_prev.append(info_current[-1])
        helper.write_soup_to_file(DATA_FILE, soup_current)

    # Comparing current and previuos info
    diff = compare_grades(info_current, info_prev)
    if diff:
        print "New grades were found. Rewriting a date_file."
        helper.write_soup_to_file(DATA_FILE, soup_current)
        return diff
    return False


if __name__ == '__main__':
    day = get_current_day()
    drv, soup = render_page()
    newGrade = check_day(day, soup)
    if newGrade:
        send_alert(newGrade)
    else:
        nothing_New(day, soup)
    drv.quit()
