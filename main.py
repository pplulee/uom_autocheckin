import datetime
import json
import random
import time

import pytz
import schedule
from selenium import webdriver
from telegram.ext import Updater, CommandHandler
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
        self.updater = Updater(config.configdata["tgbot_token"])
        self.updater.dispatcher.add_handler(CommandHandler('ping', self.ping))
        self.sendmessage("程序启动成功")
        self.updater.start_polling()

    def ping(self, bot, update):
        self.sendmessage("还活着捏")

    def sendmessage(self, text):
        self.updater.bot.send_message(chat_id=config.configdata["tgbot_userid"], text=text)


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
            driver.find_element("class name", "c-button--logout")  # 检测登出按钮
            print("已登录，状态正常")
        except BaseException:
            print("登录失效，开始登陆")
            self.login()

    def checkin(self):
        self.refresh()
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()
            print("签到完成")
            notification("完成了一次签到")
        except BaseException:
            print("未检测到现在可以签到的项目")

    def getcheckintime(self):
        self.refresh()
        classname = None
        try:
            content = driver.find_element("xpath", "//*[contains(text(),'Check-in open at ')]").text
        except BaseException:
            print("当天没有剩余任务，自动设置下一天运行")
            notification("已完成当天所有签到，自动设置下一天运行")
            schedule.clear()
            return modifytime(6, 0, 0)
        else:
            try:
                classname = driver.find_elements("class name", "u-font-bold")[2].text
            except BaseException:
                try:
                    classname = driver.find_elements("class name", "u-font-bold")[3].text
                except BaseException:
                    print("课程名抓取失败")
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
    time.sleep(60)
