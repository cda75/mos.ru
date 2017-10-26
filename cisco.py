from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from argparse import ArgumentParser
from ConfigParser import SafeConfigParser



def get_User(conFile='user.conf'):
	config = SafeConfigParser()
	config.read(conFile)
	user = config.get('cisco', 'user')
	password = config.get('cisco', 'password')
	return (user, password)


loginURL = 'https://apps.cisco.com/Commerce/home'
newSpec = 'https://apps.cisco.com/ccw/cpc/estimate/create'


driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)
driver.maximize_window()
driver.get(loginURL)

user, password = get_User()

driver.find_element_by_xpath('//*[@id="userInput"]').send_keys(user)
driver.find_element_by_xpath('//*[@id="passwordInput"]').send_keys(password)
driver.find_element_by_name('login-button').click()

parser = ArgumentParser(description='CLI for automating Cisco CCW actions')
parser.add_argument("-action", type=str, dest='action', help='Type of action: new')
args = parser.parse_args()
action = args.action
if action  == 'new':
	driver.get(newSpec)