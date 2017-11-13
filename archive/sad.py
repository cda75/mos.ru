# -*- coding: utf-8 -*-

from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from ConfigParser import SafeConfigParser
import os.path
import helper
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException


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
mail_header = (emailUser, emailPassword, SENDER, RECIPIENT, SUBJ)
DATA_FILE = config.get('sad', 'data_file')


def render_page():
    driver = webdriver.Firefox()
    driver.get(AUTH_URL)
    driver.find_element_by_name("j_username").send_keys(mosUser)
    driver.find_element_by_name("j_password").send_keys(mosPassword)
    driver.find_element_by_id('outerlogin_button').click()
    sleep(10)
    driver.get(MAIN_URL)
    driver.implicitly_wait(15)
    XPATH1 = "//a[@href='/pgu/ru/application/dogm/77060101/#show_4']"
    driver.find_element_by_xpath(XPATH1).click()
    sleep(10)
    XPATH2 = ".//*[@id='step_1']/div[3]/fieldset[1]/div/div[1]/div"
    driver.find_element_by_xpath(XPATH2).click()
    sleep(10)
    XPATH3 = ".//*[@id='step_1']/div[3]/fieldset[1]/div/div[1]/div/div/ul/li[2]"
    driver.find_element_by_xpath(XPATH3).click()
    sleep(8)
    RequestForm = "field[d.internal.RequestNumber]"
    driver.find_element_by_name(RequestForm).send_keys(RequestNumber)
    driver.find_element_by_id("D_surname").send_keys(FIO)
    driver.find_element_by_id('button_next').click()
    sleep(5)
    # element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "D_dou_info")))
    result = driver.find_element_by_id('D_dou_info')
    return (driver, result.get_attribute('innerHTML'))


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
        somethingChanged(msg)
        helper.write_json_to_file(DATA_FILE, dict_cur)
        print "Refreshing DATA_FILE........"
        return True
    else:
        return False


@helper.print_line
@helper.add_current_time
def somethingChanged(msg_txt):
    print "Oooops!!! Something new!"
    print msg_txt
    send_alert(msg_txt)


def send_alert(msg):
    print "Sending e-mail ........"
    helper.send_mail(mail_header, msg)


@helper.print_line
def print_result(info):
    for k, v in info.iteritems():
        print 'School %s \t: %s' % (k, v)


@helper.print_line
@helper.add_current_time
def nothing_new(current_state):
    print "Nothing New"
    print_result(current_state)


if __name__ == '__main__':
    driver, html_current = render_page()
    soup_current = BeautifulSoup(html_current, 'html.parser')
    info_current = create_dict_from_soup(soup_current)

    if not os.path.isfile(DATA_FILE):
        helper.write_json_to_file(DATA_FILE, info_current)
    info_prev = helper.read_json_from_file(DATA_FILE)

    somethingNew = check_new_info(info_current, info_prev)
    if somethingNew:
        print '[+] Done'
    else:
        nothing_new(info_current)

    driver.quit()
