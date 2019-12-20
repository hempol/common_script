from selenium import webdriver

import time

param={}
with open(r"C:\Users\Administrator\Desktop\smcb\bss_service\parameter","r",encoding="utf-8") as file_p:
    content=file_p.read().splitlines()
    for serch in content:
        param[serch.split(":")[0]]=(serch.split(":")[1])

broswer=webdriver.Chrome()
url="http://"+param["bss_ip"]+":"+str(param["bss_port"])
so_url="http://"+param["sdnc_ip"]+":"+str(param["sdnc_port"])
broswer.get(url)
broswer.find_element_by_name("name").send_keys(param["username"])
broswer.find_element_by_name("password").send_keys(param["password"])
broswer.find_element_by_name("vcode").click()
time.sleep(20)
broswer.find_element_by_xpath("/html/body/div/div/form/button").click()
time.sleep(3)
broswer.find_element_by_xpath('/html/body/div/div[2]/div/div/nav/ul/li[10]/a/span[2]').click()
broswer.find_element_by_xpath('html/body/div[1]/div[2]/div/div/nav/ul/li[10]/ul/li[2]/a/span').click()
time.sleep(5)
web_element=broswer.find_element_by_xpath("//form[@id='sdncId']/div/div[2]/div[6]/div/span").text
if web_element== "运行中":
    pass
else:
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[3]/div/button').click()
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[1]/div/input').clear()
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[1]/div/input').send_keys(param['sdnc_name'])
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[2]/div/input').clear()
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[2]/div/input').send_keys(param['sdnc_username'])
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[3]/div/input').clear()
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[3]/div/input').send_keys(param['sdnc_password'])
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[4]/div/input').clear()
    broswer.find_element_by_xpath('//*[@id="sdncId"]/div/div[2]/div[4]/div/input').send_keys(so_url)
    broswer.find_element_by_xpath('//*[@id="saveBtn"]').click()
    time.sleep(3)
    broswer.find_element_by_xpath('//*[@id="ngdialog1"]/div[2]/div/div/div[2]/footer/button[1]').click()