from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


ocaURL = 'https://partner.hpe.com/group/upp-emea/esm/-/link/187402'
user = 'd.chestnov@inlinegroup.ru'
password = 'Merlin75'

driver = webdriver.Firefox()
driver.maximize_window()
driver.get(ocaURL)

wait = WebDriverWait(driver, 10)

driver.find_element_by_xpath('//*[@id="USER"]').send_keys(user)
driver.find_element_by_xpath('//*[@id="PASSWORD"]').send_keys(password)
driver.find_element_by_xpath('//*[@id="sign-in-btn"]').click()

