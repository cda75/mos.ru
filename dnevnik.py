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
from argparse import ArgumentParser
from time import sleep
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText



diaryURL = 'https://www.mos.ru/pgu/ru/application/dogm/journal/'
loginURL = 'https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter?redirect=https%3A%2F%2Fwww.mos.ru%2F'
hwURL = 'https://dnevnik.mos.ru/manage/student_homeworks'
gradeURL = 'https://dnevnik.mos.ru/manage/student_journal/5140898'

CONFIG = SafeConfigParser()
conFile = 'user.conf'


def tomorrowDay():
	return (datetime.now() + timedelta(1)).strftime("%d.%m.%Y")


def get_User():
	CONFIG.read(conFile)
	user = CONFIG.get('auth', 'user')
	password = CONFIG.get('auth', 'password')
	return (user, password)


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


def send_mail(d,s,g,c):
	msg_txt = '%s\n%s\t%s\t%s' % (d,s,g,c)
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


def update_gradeDB(date, subject, grade, comment):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	try:
	    cursor.execute("INSERT INTO grades VALUES (?,?,?,?);", (date, subject, grade, comment))
	    con.commit()
	    print "Opps! New grade here!"
	    print "[+] Writing new grade to DB..........."
	    send_mail(date, subject, grade, comment)
	except sql.IntegrityError:
		pass
		#print "[-] Error writing to grade DB\t\t(already exist)\t%s : %s" %(date, subject)
	finally:
		con.close()


def check_grade(drv):
	drv.get(gradeURL)
	mainBody = drv.find_elements_by_class_name("student-journal-day")
	week = []
	for day in mainBody:
		html = day.get_attribute('innerHTML')
		soup = BeautifulSoup(html,'html.parser')
		week.append(soup)
	week = week[:-1]
	for day in week:
		date = day.find('span', class_="date").get_text()
		lessons = day.find_all('div', class_="student-journal-day-lesson")
		for lesson in lessons:
			subj = lesson.find('div', class_="column column-subject")
			if subj:
				subject = subj.find('span', class_="break-text").get_text()
				grade = lesson.find('div', class_="column column-marks")
				mark = grade.find(re.compile("^student-journal-mark"))
				if mark:
					grade = mark.get_text().strip()[0]
					weight = mark.find('span', class_="student-journal-mark-weight")
					if weight:
						weight = weight.get_text().strip()
						grade = grade[0] + ':' + weight
					comment = lesson.find('div', class_="column column-marks").find('div', class_="student-journal-mark-info")
					if comment:
						comment = comment.get_text().strip()
					update_gradeDB(date, subject, grade, comment)
	return drv


def update_hwDB(date, subject, descr, comment):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	badString = 'Описание ДЗ'.decode('utf8')
	task = (re.sub(badString,'',descr)).strip()
	try:
		cursor.execute("INSERT INTO homework VALUES (?,?,?,?);", (date, subject, task, comment))
		con.commit()
		print 'Oops! New homework found!'
		print '[+] Writing new homework to DB...........'
	except sql.IntegrityError:
		pass
		#print '[-] Error writing to homework DB\t(already exist)\t%s : %s' %(date, subject)
	finally:
		con.close()


def check_hw(drv):
	drv.get(hwURL)
	week_task = []
	homeWork = []
	tasks = drv.find_elements_by_class_name("homework-details")
	for task in tasks:
		html = task.get_attribute('innerHTML')
		soup = BeautifulSoup(html, 'html.parser')
		week_task.append(soup)
	for task in week_task:
		date = task.find('div', class_="column date-to").get_text().strip()
		subject = task.find('div', class_="column subject-name br-text").get_text().strip()
		description = task.find('div', class_="column description br-text").get_text().strip()
		comment = task.find('div', class_="column comment").get_text().strip()
		update_hwDB(date, subject, description, comment)
	return drv


def check_diary():
	drv = start()
	check_hw(check_grade(drv))
	

def print_grade():
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	print "Extracting data from DataBase.....\n"
	cursor.execute("SELECT * FROM grades")
	rows = cursor.fetchall()
	for row in rows:
		date = row[0].decode('utf8').encode('cp1251')
		subj = row[1].decode('utf8').encode('cp1251')
		grade = row[2].decode('utf8').encode('cp1251')
		info = row[3].decode('utf8').encode('cp1251')
		print "%s\t%s\t%s (%s)" %(date, grade, subj, info)
	con.close()


def print_dayHW(cur, day):
	cur.execute("SELECT subject,description FROM homework WHERE date=?", (day,))
	rows = cur.fetchall()
	for row in rows:
		for i in row:
			print i.decode('utf8').encode('cp1251'),'\t',
		print 


def print_hw(day):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	print "Extracting data from DataBase.....\n"
	if day != 'week':
		if day == '':
			day = tomorrowDay()
		print '\n',day
		print_dayHW(cursor, day)
	else:
		today = datetime.now()
		tomorrow = today + timedelta(1)
		curWeekDay = today.weekday()
		weekEnd = today + timedelta(4-curWeekDay)
		N = int(weekEnd.strftime('%d')) - int(today.strftime('%d'))
		for i in range(N):
			d = tomorrow.strftime('%d.%m.%Y')
			print '\n',d
			print_dayHW(cursor, d)
			tomorrow += timedelta(1)
	con.close()




def arg_parse():
	parser = ArgumentParser(description='API for MOS.RU Electronic Diary checking')
	parser.add_argument("--action", "-a", type=str, dest='action', choices=['grade','hw', 'update'], default='grade', help='type of action')
	parser.add_argument("--day", "-d", type=str, dest='timeFrame', default='', help='day[dd.mm.yyyy], week or skip it for tomorrow')
	args = parser.parse_args()
	return args.action, args.timeFrame


if __name__ == '__main__':
	action, timeFrame = arg_parse()
	if action == 'grade':
		print_grade()
	if action == 'hw':
		print_hw(timeFrame)
	if action == 'update':
		check_diary()
















