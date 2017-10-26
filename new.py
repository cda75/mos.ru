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



diaryURL = 'https://www.mos.ru/pgu/ru/application/dogm/journal/'
loginURL = 'https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter?redirect=https%3A%2F%2Fwww.mos.ru%2F'
hwURL = 'https://dnevnik.mos.ru/manage/student_homeworks'
homeURL = ''


def tomorrowDay():
	return (datetime.now() + timedelta(1)).strftime("%d.%m.%Y")


def get_User(conFile='user.conf'):
	config = SafeConfigParser()
	config.read(conFile)
	user = config.get('auth', 'user')
	password = config.get('auth', 'password')
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


def start(startPage=hwURL):
	user, password = get_User()
	driver = webdriver.Firefox()
	#driver.maximize_window()
	driver.implicitly_wait(12)
	driver.get(loginURL)
	driver.find_element_by_name("j_username").send_keys(user)
	driver.find_element_by_name("j_password").send_keys(password)
	driver.find_element_by_id('outerlogin_button').click()
	driver.get(diaryURL)
	driver.get(startPage)

	week_task = []
	task_list = []
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
		task_list.append(tmp)

	return task_list


def writeDB(task):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	badString = 'Описание ДЗ'.decode('utf8')
	print "Writing date to DataBase.....\n"
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
	tasks = start()
	writeDB(tasks)
	get_task_by_day()


#driver.close()













