from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from argparse import ArgumentParser
from ConfigParser import SafeConfigParser



def get_User(conFile='user.conf'):
	config = SafeConfigParser()
	config.read(conFile)
	user = config.get('hpe', 'user')
	password = config.get('hpe', 'password')
	return (user, password)


def login(URL):
	user, password = get_User()
	driver = webdriver.Firefox()
	wait = WebDriverWait(driver, 10)
	driver.maximize_window()
	driver.get(URL)
	driver.find_element_by_xpath('//*[@id="USER"]').send_keys(user)
	driver.find_element_by_xpath('//*[@id="PASSWORD"]').send_keys(password)
	driver.find_element_by_xpath('//*[@id="sign-in-btn"]').click()
	return driver


URLs = {
		'main':   'https://partner.hpe.com/group/upp-emea',
		'spec':    'https://partner.hpe.com/group/upp-emea/esm/-/link/187402',
		'cert':   'https://partner.hpe.com/group/upp-emea/esm/-/link/172903',
		'deal':   'https://partner.hpe.com/group/upp-emea/esm/-/link/179409',
		'rebate': 'https://partner.hpe.com/group/upp-emea/esm/-/link/50109',
		'user':  'https://partner.hpe.com/group/upp-emea/profile-preferences?p_p_id=prpportalpreferencesportlet_WAR_prpportalpreferencesportlet&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2&_prpportalpreferencesportlet_WAR_prpportalpreferencesportlet_action=mangeUsers',
		'status': 'https://partner.hpe.com/group/upp-emea/my-partner-ready-status'
		}


parser = ArgumentParser(description='CLI for automating HPE PPA actions')
parser.add_argument("-action", type=str, dest='action', default='spec', help='Type of action: cert, spec, deal, rebate, user, status')
args = parser.parse_args()
action = args.action



if __name__ == "__main__":

	login(URLs[action])
