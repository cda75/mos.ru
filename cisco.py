from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


loginURL = 'https://apps.cisco.com/Commerce/home'
user = 'd.chestnov'
password = 'cisco123'

driver = webdriver.Firefox()
driver.maximize_window()
driver.get(loginURL)

wait = WebDriverWait(driver, 10)

driver.find_element_by_xpath('//*[@id="userInput"]').send_keys(user)
driver.find_element_by_xpath('//*[@id="passwordInput"]').send_keys(password)
driver.find_element_by_name('login-button').click()
