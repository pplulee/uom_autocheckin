import datetime
import json
import random
import time

import pytz
import requests
import schedule
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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

        if self.configdata["wxpusher_enable"] == 1:
            self.wxpusher_enable = True
        else:
            self.wxpusher_enable = False

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
driver.set_page_load_timeout(30)


class TGbot:
    def __init__(self):
        self.updater = Updater(config.configdata["tgbot_token"])
        self.updater.dispatcher.add_handler(CommandHandler('ping', self.ping))
        self.updater.dispatcher.add_handler(CommandHandler('nextclass', self.nextclass))
        self.updater.dispatcher.add_handler(CommandHandler('nexttime', self.nexttime))
        self.sendmessage("签到程序启动成功")
        self.updater.start_polling()

    def ping(self, bot, update):
        self.sendmessage("还活着捏")

    def nextclass(self, bot, update):
        self.sendmessage(f"下节课是：{user.next_class}")

    def nexttime(self, bot, update):
        self.sendmessage(f"下节课的时间：{user.next_time}")

    def sendmessage(self, text):
        self.updater.bot.send_message(chat_id=config.configdata["tgbot_userid"], text=text)


class WXpusher:
    def __init__(self):
        self.API_TOKEN = "AT_MrNwhC7N9jbt2hmdDXxOaGPkI7OmN8WV"
        self.baseurl = f"http://wxpusher.zjiecode.com/api/send/message/?appToken={self.API_TOKEN}\
        &uid={config.configdata['wxpusher_uid']}&content="
        self.sendmessage("签到程序启动成功")

    def sendmessage(self, content):
        requests.get(f"{self.baseurl}{content}")


if config.tgbot_enable:
    tgbot = TGbot()

if config.wxpusher_enable:
    wxpusher = WXpusher()


def notification(content):
    print(content)
    if config.tgbot_enable:
        tgbot.sendmessage(content)
    if config.wxpusher_enable:
        wxpusher.sendmessage(content)


class User:
    def __init__(self):
        self.username = config.configdata["username"]
        self.password = config.configdata["password"]
        self.next_class = ""
        self.next_time = ""

    def login(self):
        driver.find_element("id", "username").send_keys(self.username)
        driver.find_element("id", "password").send_keys(self.password)
        driver.find_element("name", "submit").click()
        print("完成登录")

    def refresh(self):
        try:
            driver.get('https://my.manchester.ac.uk/MyCheckIn')
        except TimeoutException:
            timeout()
        else:
            try:
                driver.find_element("class name", "c-button--logout")  # 检测登出按钮
                # print("已登录，状态正常")
            except BaseException:
                # print("登录失效，开始登陆")
                self.login()

    def checkin(self):
        self.refresh()
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()
            notification("完成了一次签到")
        except BaseException:
            pass

    def getcheckintime(self):
        self.refresh()
        try:
            content = driver.find_element("xpath", "//*[contains(text(),'Check-in open at ')]").text
        except BaseException:
            notification("已完成当天所有签到，自动设置下一天运行")
            schedule.clear()
            self.next_class = "没有课程"
            return modifytime(6, 0, 0)
        else:
            if self.next_class == driver.find_elements("class name", "u-font-bold")[2].text:
                self.next_class = driver.find_elements("class name", "u-font-bold")[3].text
            else:
                self.next_class = driver.find_elements("class name", "u-font-bold")[2].text
            notification(f"下一节课是{self.next_class}")
            self.next_time = randomtime(content[-5:])  # 首个任务的时间
            return self.next_time


def randomtime(time):  # 随机时间
    return modifytime(int(time[:2]), int(time[3:]) + random.randrange(0, 10), random.randrange(0, 60))


def modifytime(hh, mm, ss):  # 换算时区
    time = datetime.datetime(2000, 1, 1, hh, mm, ss)
    time = config.tzlondon.localize(time)
    time = time.astimezone(config.tzlocal)
    return [time.strftime('%H:%M:%S'), f"{hh}:{mm}:{ss}"]  # 修正时区|伦敦时区


def timeout():
    notification("页面加载超时，已退出")
    driver.quit()
    exit()


def job():
    user.checkin()
    schedule.clear()
    nexttime = user.getcheckintime()
    schedule.every().day.at(nexttime[0]).do(job)
    print(f"已设置下次执行时间（本地时区）：{nexttime[0]}")
    notification(f"已设置下次执行时间：{nexttime[1]}")


user = User()
job()

while True:
    schedule.run_pending()
    time.sleep(60)
