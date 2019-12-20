# -*- coding:utf8 -*-

from selenium import webdriver
from time import sleep

username = "administrator"
password = "raisecom"
url = "http://192.168.193.43:18088"
vnfm_url = "http://127.0.0.1:9002"

driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()

#+++++++++++++++ NFVO登录 +++++++++++++++++#
sleep(2)
driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div/div/div/div/div[3]/div/div/div[1]/input").send_keys(username)
driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div/div/div/div/div[4]/div/div/div[1]/input").send_keys(password)
sleep(0.5)
driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div/div/div/div/div[5]/div/div/div[1]/div/div/div/input").send_keys('1234567890')
driver.find_element_by_xpath("/html/body/div[2]/div/div/div/form/div/div/div/div/a[2]/span/span").click()
sleep(3)
#
# #+++++++++++++++ 添加域 +++++++++++++++++#
# driver.find_element_by_xpath('//*[@id="button-1064-btnInnerEl"]').click()
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div/div/div/div/input").send_keys('SHDX')
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div/div[2]/div/div/div/div/div/div/div[2]/div/div/a[1]/span/span/span[2]").click()
# sleep(1)
# driver.find_element_by_xpath('//*[@id="button-1005-btnInnerEl"]').click()
#
# #+++++++++++++++ 注册VIM +++++++++++++++++#
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[1]/ul/li[1]/ul/li[2]/div/div/div[2]").click()
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/a[2]/span/span/span[2]").click()
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/input").send_keys("Tis")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div/div/input").send_keys("http://192.168.193.2:5000/v3")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[3]/div/div/div/input").send_keys("admin")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/input").send_keys("Raisecom@123")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/input").send_keys("admin")
# driver.find_element_by_xpath("//div/div/div/div/div/div/div[2]/div/div/div[3]/div/div/div[2]").click()
# sleep(0.5)
# driver.find_element_by_xpath('//div[contains(@id,"picker-listWrap")]/ul/li[1]').click()
# sleep(0.5)
# driver.find_element_by_xpath('//div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/a/span/span/span[2]').click()
# sleep(3)
# echo= driver.find_element_by_xpath("//div[@id='container-1003-targetEl']/div").text
# if echo == u"注册成功！":
#     print "NFVO VIM注册成功！"
# else:
#     raise Exception("NFVO VIM注册失败!")
# driver.find_element_by_xpath('//div[2]/div[2]/div/div/a/span/span/span[2]').click()
# sleep(1)
#
# #+++++++++++++++ 注册VNFM +++++++++++++++++#
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[1]/ul/li[1]/ul/li[3]/div/div/div[2]").click()
# driver.find_element_by_xpath('//div[contains(@id,"VNFMMngView")]/div[1]/div[2]/div[1]/span/div/div/a[2]/span/span/span[2]').click()
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[1]/div/div/div/input").send_keys("VNFM1")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[2]/div/div/div/input").send_keys(vnfm_url)
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[3]/div/div/div/input").send_keys("admin")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/input").send_keys("admin")
# driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/input").send_keys("default_tenant")

#+++++++++++++++ 上传NS模板 +++++++++++++++++#
# driver.find_element_by_xpath("//li[2]/ul/li/div/div/div[2]").click()
# # driver.find_element_by_xpath("//div[2]/div/div[2]/div/div/div/a[2]/span/span/span[2]").click()
# # driver.find_element_by_xpath("//div[2]/div[2]/div/div/div/div/div/div/div/div/div/fieldset/div/div/div/div/div/div/div/div/div/div/div/div/div/input").send_keys("NS_wxl")
# # driver.find_element_by_xpath("//fieldset/div/div/div/div/div/div/div/div/div/div[2]/div/div/div/input").send_keys("1")
# # raw_input("请选择上传文件：")
# driver.find_element_by_xpath("//div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/a/span/span/span[2]").click()
# sleep(5)

#+++++++++++++++ 部署 +++++++++++++++++#
driver.find_element_by_xpath("//li[2]/ul/li[2]/div/div/div[2]").click()
sleep(0.4)
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[1]/div[2]/div[1]/div/div/a[2]/span/span/span[2]").click()
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[1]/div/div/div[2]").click()
sleep(0.5)
#driver.find_element_by_xpath('//div[contains(@id,"picker-listWrap")]/ul/li').click()
driver.find_element_by_xpath(".//li[text()='ns']").click()
driver.find_element_by_xpath('html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/fieldset/div/div/div/div/div/div/div[3]/div/div/div[2]').click()
sleep(1)
#driver.find_element_by_xpath(".//li[text()='VNFM']").click()

driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div/div[2]/div/div/div/div/div/div/input").send_keys("ns01")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/input").send_keys("wdx_ians_d2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[3]/div/div/div/input").send_keys("compute-2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/input").send_keys("wdx_ians_d2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[3]/div/div/div[2]/div/div/div/input").send_keys("iANS_mb")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div/div/div/input").send_keys("wdx_ians_d2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[3]/div/div/div/input").send_keys("50")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[3]/div/div/div[3]/div/div/div/input").send_keys("iANS_sanqi")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[5]/div/div/div/input").send_keys("manager")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div/input").send_keys("vcpe_vans_wdx")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[2]/div[2]/div/div/div/div/div/div/div[3]/div/div/div[4]/div/div/div/input").send_keys("Internet_vlan43")

driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[1]/div/div/div/input").send_keys("wdx_iedge_d2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[3]/div/div/div/input").send_keys("compute-2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[2]/div/div/div/input").send_keys("wdx_iedge_d2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[3]/div/div/div[2]/div/div/div/input").send_keys("vCPE_mb")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div/div/div/input").send_keys("wdx_iedge_d2")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[3]/div/div/div/input").send_keys("10")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[3]/div/div/div[3]/div/div/div/input").send_keys("VCPE_10G")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[5]/div/div/div/input").send_keys("manager")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[2]/div/div/div[4]/div/div/div/input").send_keys("Internet_vlan43")
driver.find_element_by_xpath("html/body/div[2]/div[2]/div[3]/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div[1]/div/div/div[4]/div[2]/div/div/div/div/div/div/div[3]/div/div/div[4]/div/div/div/input").send_keys("vcpe_vans_wdx")

