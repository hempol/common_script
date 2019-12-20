# -*- coding:utf8 -*-

from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains

username = "administrator"
password = "raisecom"
url = "http://192.168.193.30:18088"
vnfm_url = "http://192.168.193.28:90021"

driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()

sleep(2)
driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div/div/div/div/div[3]/div/div/div[1]/input").send_keys(username)
driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div/div/div/div/div[4]/div/div/div[1]/input").send_keys(password)
sleep(0.5)
driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div/div/div/div/div[5]/div/div/div[1]/div/div/div/input").send_keys('1234567890')
driver.find_element_by_xpath("/html/body/div[2]/div/div/div/form/div/div/div/div/a[2]/span/span").click()
sleep(3)

driver.find_element_by_xpath("//li[2]/ul/li[2]/div/div/div[2]").click()
sleep(0.4)
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/a[2]/span/span/span[2]").click()
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[2]").click()
sleep(0.5)
driver.find_element_by_xpath('//div[contains(@id,"picker-listWrap")]/ul/li').click()
driver.find_element_by_xpath('html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[3]/div/div/div[2]').click()
sleep(0.5)

ul = driver.find_element_by_xpath('//div[contains(@id,"ext-element")]')
print ul
lis = ul.find_elements_by_xpath(".//li[text()='VNFM']")
len(lis)    # 有多少个li
print lis
