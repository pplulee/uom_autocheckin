import random

from selenium import webdriver
import time
import schedule

opt = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=opt)

# 第一行加username，第二行加password
details = open('account.txt').read().splitlines()


class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.isLogin = False

    def login(self):
        driver.find_element_by_id('username').send_keys(self.username)
        print("输入账号")
        driver.find_element_by_id('password').send_keys(self.password)
        print("输入密码")
        driver.find_element_by_name('submit').click()
        self.isLogin = True
        print("完成登录")

    def refresh(self):
        print("打开URL")
        driver.get('https://my.manchester.ac.uk/MyCheckIn')
        try:
            driver.find_element_by_class_name('c-button')  # 检测登出按钮
            print("已登录，状态正常")
        except BaseException:
            print("登录失效，开始登陆")
            self.login()

    def checkin(self):
        self.refresh()
        try:
            driver.find_element_by_name('StudentSelfCheckinSubmit').click()
            print("签到完成")
        except BaseException:
            print("未检测到需要签到的项目")

    def getcheckintime(self):
        self.refresh()
        try:
            content = driver.find_element_by_xpath("//*[contains(text(),'Check-in open at ')]").text
        except BaseException:
            print("未检测到需要签到的项目，直接结束进程")
            exit()
        else:
            return content[-5:]  # 首个任务的时间


def modifytime(time):  # 换算时区+随机秒数
    if (hh := int(time[:2]) + 7) > 24:
        hh = 24 - hh
    hh = str(hh)
    mm = str(int(time[3:]) + random.randrange(0, 10))
    ss = str(random.randrange(0, 60))
    return f"{hh}:{mm}:{ss}"


def job():
    userobj.checkin()
    schedule.clear()
    schedule.every().day.at(nexttime := modifytime(userobj.getcheckintime())).do(job)
    print("已设置下次执行时间：", nexttime)


userobj = user(details[0], details[1])
job()
while True:
    schedule.run_pending()
    time.sleep(1)
