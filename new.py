# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from sys import stdout
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
import sqlite3 as sql
import re
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser 
from time import sleep
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText



diaryURL = 'https://www.mos.ru/pgu/ru/application/dogm/journal/'
loginURL = 'https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter?redirect=https%3A%2F%2Fwww.mos.ru%2F'
hwURL = 'https://dnevnik.mos.ru/manage/student_homeworks'
homeURL = 'https://dnevnik.mos.ru/manage/student_journal/5140898'

CONFIG = SafeConfigParser()
conFile = 'user.conf'


def tomorrowDay():
	return (datetime.now() + timedelta(1)).strftime("%d.%m.%Y")


def get_User():
	CONFIG.read(conFile)
	user = CONFIG.get('auth', 'user')
	password = CONFIG.get('auth', 'password')
	return (user, password)


def get_task_by_day(day=''):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	print "Extracting data from DataBase.....\n"
	if not day:
		day = tomorrowDay()
	cursor.execute("SELECT subject,description FROM dnevnik WHERE d_to=?", (day,))
	rows = cursor.fetchall()
	print
	for row in rows:
		for i in row:
			print i.decode('cp1251'),'\t\t',
		print 
	con.close()


def start():
	user, password = get_User()
	driver = webdriver.Firefox()
	#driver.maximize_window()
	driver.implicitly_wait(15)
	driver.get(loginURL)
	driver.find_element_by_name("j_username").send_keys(user)
	driver.find_element_by_name("j_password").send_keys(password)
	driver.find_element_by_id('outerlogin_button').click()
	driver.get(diaryURL)
	sleep(3)
	return driver


def get_homeworks(driver):
	driver.get(hwURL)
	week_task = []
	homeWork = []
	tasks = driver.find_elements_by_class_name("homework-details")
	for task in tasks:
		html = task.get_attribute('innerHTML')
		soup = BeautifulSoup(html, 'html.parser')
		week_task.append(soup)

	for task in week_task:
		spans = task.find_all('span')
		tmp = []
		for span in spans:
			tmp.append(span.get_text())
		homeWork.append(tmp)
#	sleep(3)
	return homeWork


def get_grades(driver):
	driver.get(homeURL)
	mainBody = driver.find_elements_by_class_name("student-journal-day")
	week = []
	for day in mainBody:
		html = day.get_attribute('innerHTML')
		soup = BeautifulSoup(html,'html.parser')
		week.append(soup)

	for day in week:
		date = day.find('span', class_="date").get_text()
		print '\n', date
		lessons = day.find_all('div', class_="student-journal-day-lesson")
		for lesson in lessons:
			subj = lesson.find('div', class_="column column-subject")
			if subj:
				subject = subj.find('span', class_="break-text").get_text()
				print subject, '\t', 
				grades = lesson.find('div', class_="column column-marks").find('span', class_="student-journal-mark")	
				if grades:
					grade = grades.get_text()
					print grade,
					comment = lesson.find('div', class_="column column-marks").find('div', class_="student-journal-mark-info")
					if comment:
						print comment.get_text()
						comment = comment.get_text()
					check_grade((date, subject, grade, comment))
				print


def check_grade(grade):
	if not grade_exist(grade):
		send_alert(grade)
		

def grade_exist(grade):
	d,s,g,c = grade
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
        try:
	    cursor.execute("INSERT INTO grades VALUES (?,?,?,?);", (d,s,g,c))
            con.commit()
            con.close()
            print '[+] Write new grade to DB......'
            return False
        except sql.IntegrityError:
            con.close()
            return True


def send_mail(msg_txt):
	CONFIG.read(conFile)
	eUser = CONFIG.get('email', 'user')
	ePassword = CONFIG.get('email', 'password')
	sender = CONFIG.get('email', 'sender')
	subject = CONFIG.get('email', 'subject')
	recipient = CONFIG.get('email', 'recipients')
	msg = MIMEMultipart()
	msg['From'] = sender
	msg['To'] = recipient
	msg['Subject'] = subject
	msg.attach(MIMEText(msg_txt.encode('utf-8'),'plain'))
	try:
		server = SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(eUser, ePassword)
		server.sendmail(sender, recipient, msg.as_string())
		print '[+] Email successfully sent'
	except:
		print "[-] Error sending email"
	finally:
		server.quit()


def send_alert(grade):
	d,s,g,c = grade
	msg_txt = '%s\n%s\t%s\t%s' % (d,s,g,c)
	send_mail(msg_txt)
	
	
def writeDB(task):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	badString = 'Описание ДЗ'.decode('utf8')
	print "Writing information to DataBase.....\n"
	for t in task:
		df = t[0].encode('cp1251')
		dt = t[1].encode('cp1251')
		subj = t[2].encode('cp1251')
		req = ' '
		descr = t[4].encode('cp1251')
		descr = (re.sub(badString.encode('cp1251'),'',descr)).strip()
		dur = t[5].encode('cp1251')
		comm = ' '
		cursor.execute("INSERT OR IGNORE INTO dnevnik VALUES (?,?,?,?,?,?,?);", (df,dt,subj,req,descr,dur,comm))
		con.commit()
	con.close()



if __name__ == '__main__':
	drv = start()
	get_grades(drv)













