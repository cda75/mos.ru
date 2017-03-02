# -*- coding: utf-8 -*-

from time import sleep, strftime, localtime
import smtplib
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from ConfigParser import SafeConfigParser
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
import os.path
import platform



MAIN_URL = 'https://www.mos.ru/pgu/ru/services/link/1742/?utm_source=mos&utm_medium=ek&utm_referrer=mos.ru&utm_campaign=popular&utm_term=733533'
AUTH_URL = 'https://www.mos.ru/api/oauth20/v1/frontend/json/ru/process/enter?redirect=https://www.mos.ru'
CONF_FILE = 'user.conf'

config = SafeConfigParser()
config.read(CONF_FILE)
mosUser = config.get('auth', 'user')
mosPassword = config.get('auth', 'password')
emailUser = config.get('email', 'user')
emailPassword = config.get('email', 'password')
RequestNumber = config.get('sad', 'ReqNum')
FIO = config.get('sad', 'fio').decode('utf-8')
SENDER = config.get('email', 'sender')
SUBJ = config.get('email', 'subject')
RECIPIENT = config.get('email', 'recipients')
DATA_FILE = config.get('sad', 'data_file')

OS = platform.system()
isLinux = (OS == 'Linux')
isWindows = (OS == 'Windows')


def render_page():
    driver = webdriver.Firefox()
    driver.get(AUTH_URL)
    driver.find_element_by_name("j_username").send_keys(mosUser)
    driver.find_element_by_name("j_password").send_keys(mosPassword)
    driver.find_element_by_id('outerlogin_button').click()
    sleep(5)
    driver.get(MAIN_URL)
    driver.implicitly_wait(15)
    XPATH1 = "//a[@href='/pgu/ru/application/dogm/77060101/#show_4']"
    driver.find_element_by_xpath(XPATH1).click()
    sleep(8)
    XPATH2 = ".//*[@id='step_1']/div[3]/fieldset[1]/div/div[1]/div"
    driver.find_element_by_xpath(XPATH2).click()
    sleep(7)
    XPATH3 = ".//*[@id='step_1']/div[3]/fieldset[1]/div/div[1]/div/div/ul/li[2]"
    driver.find_element_by_xpath(XPATH3).click()
    #sleep(7)
    RequestForm = "field[d.internal.RequestNumber]"
    driver.find_element_by_name(RequestForm).send_keys(RequestNumber)
    driver.find_element_by_id("D_surname").send_keys(FIO)
    driver.find_element_by_id('button_next').click()
    sleep(8)
    #   element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "D_dou_info")))
    result = driver.find_element_by_id('D_dou_info')
    return (driver, result.get_attribute('innerHTML'))


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


def read_json_from_file():
    with open(DATA_FILE) as f:
        return json.load(f)


def write_json_to_file(info):
    with open(DATA_FILE, 'w') as f:
        f.write(json.dumps(info))


def create_dict_from_soup(soup):
    info = {}
    pattern = re.compile(ur'\d+', re.UNICODE)
    for block in soup.find_all('div', class_='wrap'):
        s = block.find('span', class_='tpl_info_text').get_text()
        q = block.find('span', class_='tpl_info_queque').get_text()
        school = pattern.search(s).group()
        queque = pattern.search(q).group()
        info[school] = queque
    return info


def check_new_info(dict_cur, dict_prev):
    diff = [k for k in dict_cur if dict_cur[k] != dict_prev[k]]
    if diff:
        msg = ''
        for k in diff:
            msg += 'School %s\t: %s ---> %s\n' % (k, dict_prev[k], dict_cur[k])
        print 'Oooops! Something changed'
        print msg
        send_mail(msg)
        write_json_to_file(dict_cur)
        return True
    else:
        return False


@print_line
def print_result(info):
    for k, v in info.iteritems():
        print 'School %s \t: %s' % (k, v)


@print_line
@add_current_time
def nothing_new(current_state):
    print "Nothing New"
    print_result(current_state)


if __name__ == '__main__':
    driver, html_current = render_page()
    soup_current = BeautifulSoup(html_current, 'html.parser')
    info_current = create_dict_from_soup(soup_current)

    if not os.path.isfile(DATA_FILE):
        write_json_to_file(info_current)
    info_prev = read_json_from_file()

    somethingNew = check_new_info(info_current, info_prev)
    if somethingNew:
        print '[+] Done'
    else:
        nothing_new(info_current)

    driver.quit()
