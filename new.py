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



def save_week_to_file(fname, soup):
	with open(fname, 'w') as f:
		print "[+] Writing new info to week file........."
		f.write(soup.encode('utf-8'))

def read_week_from_file(fname):
    with open(fname) as f:
    	print "[+] Reading info from week file..........."
    	return BeautifulSoup(f.read(), 'html.parser')


def get_task_by_day(day):
	con = sql.connect("mosru.db")
	con.text_factory = str
	cursor = con.cursor()
	cursor.execute("SELECT subject,description FROM dnevnik WHERE d_to=?", (day,))
	rows = cursor.fetchall()
	print
	for row in rows:
		for i in row:
			print i.decode('cp1251'),'\t\t',
		print 
	con.close()

'''
mainURL = 'https://www.mos.ru'
diaryURL = 'https://www.mos.ru/pgu/ru/application/dogm/journal/'
loginURL = 'https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter?redirect=https%3A%2F%2Fwww.mos.ru%2F'
hwURL = 'https://dnevnik.mos.ru/manage/student_homeworks'

CODING = stdout.encoding

user = 'dchestnov@mail.ru'
password = 'Merlin75'

driver = webdriver.Firefox()
#driver.maximize_window()
driver.implicitly_wait(12)

driver.get(loginURL)
driver.find_element_by_name("j_username").send_keys(user)
driver.find_element_by_name("j_password").send_keys(password)
driver.find_element_by_id('outerlogin_button').click()
driver.get(diaryURL)
driver.get(hwURL)

week_task = []
tasks = driver.find_elements_by_class_name("homework-details")

for task in tasks:
	html = task.get_attribute('innerHTML')
	soup = BeautifulSoup(html, 'html.parser')
	week_task.append(soup)

task_list = []

for task in week_task:
	spans = task.find_all('span')
	tmp = []
	for span in spans:
		tmp.append(span.get_text())
	task_list.append(tmp)


con = sql.connect("mosru.db")
con.text_factory = str
cursor = con.cursor()

for t in task_list:
	df = t[0].encode('cp1251')
	dt = t[1].encode('cp1251')
	subj = t[2].encode('cp1251')
	req = ' '
	descr = t[4].encode('cp1251')
	descr = re.sub('Описание ДЗ'.decode('utf-8').encode('cp1251'),'',descr)
	dur = t[5].encode('cp1251')
	comm = ' '
	cursor.execute("INSERT OR IGNORE INTO dnevnik VALUES (?,?,?,?,?,?,?);", (df,dt,subj,req,descr,dur,comm))
	con.commit()

'''

get_task_by_day('25.10.2017')

#driver.close()













