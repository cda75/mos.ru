# -*- coding: utf-8 -*-


import smtplib
import json
import platform
from bs4 import BeautifulSoup
from time import strftime, localtime
import os.path
from sys import stdout
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime, timedelta


# Main Class description
class TimeTable(object):
    mosURL = 'https://pgu.mos.ru/ru/application/dogm/journal/#step_1'
    CODING = stdout.encoding

    def __init__(self, week='', mosUser='', mosPassword=''):
        self.__mosUser = mosUser
        self.__mosPassword = mosPassword
        self.weekData = {}
        self.set_week(week)
        if os.path.isfile(self.weekFile):
            self.weekSoup = self.__read_week_from_file()
            if len(self.weekSoup) == 0:
                print '[-] File is empty, running page scruup'
                self.start()
                self.__save_week_to_file()
                self.stop()
        else:
            print "[-] Week File is absent!"
            print "[i] Start writing new week file"
            self.start()
            self.__save_week_to_file()
            self.stop()

    def set_week(self, week=None):
        today = datetime.now()
        self.today = today.strftime("%d.%m")
        curWeekday = today.weekday()
        weekStart = today - timedelta(curWeekday)
        if week == 'prev':
            weekStart -= timedelta(7)
        elif week == 'next':
            weekStart += timedelta(7)
        self.weekStart = weekStart.strftime("%d.%m.%Y")
        self.weekFile = weekStart.strftime("%d-%m-%y") + '.data'
        self.tomorrow = (today + timedelta(1)).strftime("%d.%m")
        self.yestarday = (today - timedelta(1)).strftime("%d.%m")

    def set_day(self, day):
        self.day = day

    def start(self):
        print "[i] Start grabing info from web page......................"
        driver = webdriver.Firefox()
        driver.get(self.mosURL)
        wait = WebDriverWait(driver, 15)
        elem1 = "//a[@class='chosen-single']/span[.='K1617']"
        elem2 = "//div[@class='b-diary-st__body']"
        driver.find_element_by_name("j_username").send_keys(self.__mosUser)
        driver.find_element_by_name("j_password").send_keys(self.__mosPassword)
        driver.find_element_by_id('outerlogin_button').click()
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, elem1)))
            driver.find_element_by_id("button_next").click()
            diary = wait.until(EC.presence_of_element_located((By.XPATH, elem2)))
            html = diary.get_attribute('innerHTML')
            self.weekSoup = BeautifulSoup(html, 'html.parser')
            self.__driver = driver
            print "[+] Web page successfully grabbed"
            '''
            if len(self.weekSoup) > 0:
                self.__save_week_to_file()
            '''
        except (NoSuchElementException, TimeoutException):
            print "[-] Element was not found or timeout treshold was reached"

    def stop(self):
        print "[i] Closing current session.........."
        self.__driver.quit()

    def __save_week_to_file(self):
        with open(self.weekFile, 'w') as f:
            print "[+] Writing new info to week file........."
            f.write(self.weekSoup.encode('utf-8'))

    def __read_week_from_file(self):
        with open(self.weekFile) as f:
            print "[+] Reading info from week file..........."
            return BeautifulSoup(f.read(), 'html.parser')

    def __get_nextWeek(self, driver):
        pass

    def __get_weekStart(self, day=None):
        if not day:
            return self.weekStart
        year = datetime.now().strftime("%Y")
        dt_str = day + '.' + year
        dt = datetime.strptime(dt_str, "%d.%m.%Y").date()
        dt_week = dt.weekday()
        week_start = dt - timedelta(dt_week)
        return week_start.strftime("%d.%m.%y")

    def __get_day(self, day=None, soup=None):
        if not soup:
            soup = self.weekSoup
        divs = soup.find_all('div', class_='b-diary-week__column')
        if not day:
            day = self.today
        for div in divs:
            tmp = div.find('span', class_='b-diary-date')
            date = tmp.get_text()
            if date == day:
                res = []
                lines = div.find_all('div', class_='b-dl-table__list')
                for line in lines:
                    if line.contents[3].span.string:
                        res.append(line)
                return res
        else:
            print '[-] Ooops! Block with date %s not found' % day

    def print_day(self, day=None):
        pattern = 'Иностранный'.decode('utf-8')
        data_list = []
        if day == 'tomorrow' or day == 'next':
            day = self.tomorrow
        elif day == 'yestarday' or day == 'prev':
            day = self.yestarday
        elif not day:
            day = self.today
        lines = self.__get_day(day)
        print "-----------------------------------"
        print day, ':'
        for line in lines:
            columns = line.find_all('div', class_='b-dl-td_column')
            tmp = []
            for col in columns:
                txt = col.find('span').text
                if pattern in txt:
                    txt = 'Немецкий язык'.decode('utf-8')
                tmp.append(txt.encode(self.CODING))
            print "{num:3} {subj:32} {grade:6} {task:65} {comment:15}".format(num=tmp[0], subj=tmp[1], task=tmp[2], grade=tmp[3], comment=tmp[4])
            data_list.append(tmp)
        return data_list

    def print_week(self, week=None):
        pass

    def __compare_grades(self, list_cur, list_prev):
        diffs = []
        for i in range(len(list_cur)):
            subj = list_cur[i]['subj']
            grade_cur = list_cur[i]['grade']
            grade_prev = list_prev[i]['grade']
            if grade_cur != grade_prev:
                diffs.append((subj, grade_cur))
        return diffs

    def __day_to_dict(self, day, soup):
        lines = self.__get_day(day, soup)
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

    def check_dayGrade(self, day=None):
        if not day:
            day = self.today
        # Read info from previous try
        soup_prev = self.weekSoup
        info_prev = self.__day_to_dict(day, soup_prev)
        print "[+] Start checking grades for date: %s" % day
        self.start()
        soup_current = self.weekSoup
        info_current = self.__day_to_dict(day, soup_current)
        self.stop()
        # Cheking If something were added to the current Schedule
        if len(info_current) > len(info_prev):
            print "New lessons were added from the last time"
            info_prev.append(info_current[-1])
            self.__save_week_to_file()
        # Comparing current and previuos info
        diff = self.__compare_grades(info_current, info_prev)
        if diff:
            print "New grades were found. Rewriting a date_file"
            self.__save_week_to_file()
            self.print_day(day)
            return diff
        print "No new grades"
        self.print_day(day)



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
