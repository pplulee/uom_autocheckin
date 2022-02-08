import datetime
import json
import random
import time

import pytz
import schedule
import telegram
from selenium import webdriver
from tzlocal import get_localzone


class Config:
    def __init__(self):
        configfile = open("config.json", "r")
        self.configdata = json.loads(configfile.read())
        configfile.close()
        if self.configdata["webdriver"] == "local":  # 如果webdriver为local，则使用本地
            self.isremote = False
        else:
            self.isremote = True

        if self.configdata["tgbot_enable"] == 1:
            self.tgbot_enable = True
        else:
            self.tgbot_enable = False

        self.tzlondon = pytz.timezone("Europe/London")  # Time zone
        self.tzlocal = get_localzone()


config = Config()
options = webdriver.ChromeOptions()
if config.isremote:
    options.add_argument("no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Remote(command_executor=config.configdata["webdriver"],
                              options=options)
else:
    driver = webdriver.Chrome(options=options)


class TGbot:
    def __init__(self):
        self.bot = telegram.Bot(token=config.configdata["tgbot_token"])
        self.sendmessage("自动签到启动成功")

    def sendmessage(self, content):
        self.bot.send_message(text=content, chat_id=int(config.configdata["tgbot_userid"]))


if config.tgbot_enable:
    tgbot = TGbot()


def notification(content):
    if config.tgbot_enable:
        tgbot.sendmessage(content)


class User:
    def __init__(self):
        self.username = config.configdata["username"]
        self.password = config.configdata["password"]
        self.isLogin = False

    def login(self):
        driver.find_element("id", "username").send_keys(self.username)
        print("输入账号")
        driver.find_element("id", "password").send_keys(self.password)
        print("输入密码")
        driver.find_element("name", "submit").click()
        self.isLogin = True
        print("完成登录")

    def refresh(self):
        print("打开URL")
        driver.get('https://my.manchester.ac.uk/MyCheckIn')
        try:
            driver.find_element("class name", "c-button")  # 检测登出按钮
            print("已登录，状态正常")
        except BaseException:
            print("登录失效，开始登陆")
            self.login()

    def checkin(self):
        self.refresh()
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()
            print("签到完成")
            notification("完成了一次签到")  # 加入签到项目的名称
        except BaseException:
            print("未检测到需要签到的项目")

    def getcheckintime(self):
        self.refresh()
        try:
            content = driver.find_element("xpath", "//*[contains(text(),'Check-in open at ')]").text
        except BaseException:
            print("当天没有剩余任务，自动设置下一天运行")
            notification("已完成当天所有签到，自动设置下一天运行")
            schedule.clear()
            return modifytime(0, 0, 0)
        else:
            classname = driver.find_element("xpath", '//*[@id="skip-links-main-content"]/div[3]/div/div/div[4]/div[''1'
                                                     ']/div/div[1]/p').text
            print(f"下一节课是{classname}")
            notification(f"下一节课是{classname}")
            return randomtime(content[-5:])  # 首个任务的时间


def randomtime(time):  # 随机时间
    hh = int(time[:2])
    mm = int(time[3:]) + random.randrange(0, 10)
    ss = random.randrange(0, 60)
    return modifytime(hh, mm, ss)


def modifytime(hh, mm, ss):  # 换算时区
    time = datetime.datetime(2000, 1, 1, hh, mm, ss)
    time = config.tzlondon.localize(time)
    time = time.astimezone(config.tzlocal)
    return time.strftime('%H:%M:%S')


def job():
    user.checkin()
    schedule.clear()
    schedule.every().day.at(nexttime := user.getcheckintime()).do(job)
    print(f"已设置下次执行时间：{nexttime}")
    notification(f"已设置下次执行时间：{nexttime}")


user = User()
job()

while True:
    schedule.run_pending()
    time.sleep(1)
