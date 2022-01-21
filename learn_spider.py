import time
from selenium import webdriver
browser=webdriver.Chrome()#会打开浏览器
browser.get('https://www.baidu.com/')
input=browser.find_element_by_id('kw')#找百度的输入框
print(input)
input.send_keys('python')
input=browser.find_element_by_id('su').click()#回车
time.sleep(10)
browser.close()#关闭浏览器



