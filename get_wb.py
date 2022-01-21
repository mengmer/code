import re
import time

import pandas as pd
from lxml import etree
from selenium import webdriver

# pip install webdriver_manager
# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(ChromeDriverManager().install())
# 自动安装chromedriver
# driver = webdriver.Chrome()
# 测试chrome是否导入成功

# windows用户
CHROME_DRIVER = r'D:\program\conda\chromedriver.exe'  # 机器上chromedriver路径
# CHROME_DRIVER = 'C:/python-bit-2018/driver/chromedriver2.41.exe' #Thinkpad地址
# mac/linux用户
# CHROME_DRIVER = './driver/chromedriver2.42'

CHROME_OPTIONS = webdriver.ChromeOptions()
# 配置浏览器是否显示图片，不显示图片可以加快抓取。1:显示； 2：不显示
prefs = {"profile.managed_default_content_settings.images": 1}
CHROME_OPTIONS.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=CHROME_OPTIONS)


def login_weibo(driver_weibo):
    # 判断是否需要登录
    if driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[3]/div/div[1]/div/a[1]'):
        driver.find_element_by_xpath('//*[@id="app"]/div[1]/div[1]/div/div[1]/div/div/div[3]/div/div[1]/div/a[1]').click()
        driver_weibo.find_element_by_xpath('//*[@id="app"]/div[4]/div[1]/div/div[2]/div/div/div[5]/a[1]').click()
        driver_weibo.find_element_by_xpath('//*[@id="loginname"]').send_keys('17779149808')
        driver_weibo.find_element_by_name('enter_psw').send_keys('Mengsjx...')
        driver_weibo.find_element_by_class_name('W_btn_a_btn_32px').click()


df_railway = pd.DataFrame(columns=['日期', '昨日旅客', '今日预计旅客'])
for page in range(1, 7):
    df = pd.DataFrame(columns=['日期', '昨日旅客', '今日预计旅客'])
    driver.get(f'https://weibo.com/tlshz?is_search=1&visible=0&is_all=1&'
               f'key_word=%23%E8%BF%90%E8%BE%93%E8%B5%84%E8%AE%AF%23&is_tag=0&profile_ftype=1&page={page}#feedtop')
    if page == 1:
        time.sleep(10)  # 初次打开比较卡，所以先停10s
        # login_weibo(driver)
    else:
        time.sleep(4)
    wait_num = 0
    # while 1:
    #     driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # 下拉框拉到底，加载之前的微博
    #     # 判断翻页按钮是否可用，若可用，说明已经见底，若不可用，当前页面还有消息未加载，sleep数秒后继续往下拉
    #     try:
    #         if driver.find_element_by_class_name('W_pages').is_enabled():  # 判断下一页按钮是否可用，若可用，说明翻到底了
    #             break
    #     except:
    #         if wait_num >= 5:
    #             driver.refresh()  # 等待5次还未加载完说明页面卡顿，刷新
    #             wait_num = 0
    #         wait_num += 1
    #         time.sleep(3)

    html = driver.page_source  # 获取网页内容
    tree = etree.HTML(html)  # 对文章内容的网页进行解析
    # 读取所有微博文字内容部分，并只保留包含全站发送旅客字段的内容
    content = [str(x) for x in tree.xpath("//div[@class='WB_text W_f14']/text()") if '全站发送旅客' in x]
    passengers_yestoday = [re.findall("昨日全站发送旅客(.*?)万", x)[0] for x in content]
    passengers_predict = [re.findall("预计发送旅客(.*?)万", x)[0] for x in content]
    dates = [re.findall("今天是(.*?)年(.*?)月(.*?)日", x)[0] for x in content]
    dates = [f"{x[0]}{x[1].zfill(2)}{x[2].zfill(2)}" for x in dates]
    df['日期'] = dates
    df['昨日旅客'] = passengers_yestoday
    df['今日预计旅客'] = passengers_predict
    df_railway = pd.concat([df_railway, df], ignore_index=True)

df_railway['日期'] = df_railway['日期'].astype('int')
df_railway.sort_values(by='日期', inplace=True)
df_railway.to_excel('旅客.xlsx', index=False)


df_weather = pd.DataFrame(columns=['日期', '日间天气', '夜间天气', '日间气温', '夜间气温', '日间风力', '夜间风力'])
months = [202103, 202102, 202101, 202012, 202011, 202010, 202009, 202008]
for month in months:
    reobj = re.compile('\d+')
    df = pd.DataFrame(columns=['日期', '日间天气', '夜间天气', '日间气温', '夜间气温', '日间风力', '夜间风力'])
    driver.get(f'http://www.tianqihoubao.com/lishi/shanghai/month/{month}.html')
    time.sleep(4)
    html = driver.page_source  # 对文章内容的网页进行解析
    tree = etree.HTML(html)
    col_date = [''.join(reobj.findall(x.text)) for x in tree.xpath(f'//tr/td[1]/a')]
    col_weather = [x.text.replace('\n', '').replace(' ', '').strip() for x in tree.xpath(f'//tr/td[2]')][1:]
    col_weather_1 = [x.split('/')[0] for x in col_weather]
    col_weather_2 = [x.split('/')[1] for x in col_weather]

    col_temp = [x.text.replace('\n', '').replace(' ', '').replace('℃', '').strip()
                for x in tree.xpath(f'//tr/td[3]')][1:]
    col_temp1 = [x.split('/')[0] for x in col_temp]
    col_temp2 = [x.split('/')[1] for x in col_temp]

    col_wind = [x.text.replace('\n', '').replace(' ', '').strip() for x in tree.xpath(f'//tr/td[4]')][1:]
    col_wind1 = [''.join(reobj.findall(x.split('/')[0])) for x in col_wind]
    col_wind2 = [''.join(reobj.findall(x.split('/')[1])) for x in col_wind]
    df['日期'] = col_date
    df['日间天气'] = col_weather_1
    df['夜间天气'] = col_weather_2
    df['日间气温'] = col_temp1
    df['夜间气温'] = col_temp2
    df['日间风力'] = col_wind1
    df['夜间风力'] = col_wind2
    df_weather = pd.concat([df_weather, df], ignore_index=True)

df_weather['日期'] = df_railway['日期'].astype('int')
df_weather.sort_values(by='日期', inplace=True)
df_weather.to_excel('天气.xlsx', index=False)
