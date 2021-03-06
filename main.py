import argparse
import datetime
import json
import logging
import random
import time

import pytz
import requests
import schedule
from selenium import webdriver
from telegram.ext import Updater, CommandHandler
from tzlocal import get_localzone

parser = argparse.ArgumentParser(description="configuration file path")
parser.add_argument("--config_path", default="")
args = parser.parse_args()


class Config:
    def __init__(self):
        configfile = open("config.json" if args.config_path == "" else args.config_path, "r")
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


def setup_driver():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/101.0.4951.54 Safari/537.36")
    if config.isremote:
        driver = webdriver.Remote(command_executor=config.configdata["webdriver"], options=options)
    else:
        driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)


class TGbot:
    def __init__(self):
        self.updater = Updater(config.configdata["tgbot_token"])
        self.updater.dispatcher.add_handler(CommandHandler('ping', self.ping))
        self.updater.dispatcher.add_handler(CommandHandler('nextclass', self.nextclass))
        self.updater.dispatcher.add_handler(CommandHandler('nexttime', self.nexttime))
        self.updater.start_polling()

    def ping(self, bot, update):
        info("用户通过Telegram发出Telegram")
        self.sendmessage("还活着捏")

    def nextclass(self, bot, update):
        info("telegram发出下节课信息")
        self.sendmessage(f"下节课是：{user.next_class}")

    def nexttime(self, bot, update):
        info("telegram发出下节课时间")
        self.sendmessage(f"下节课的时间：{user.next_time}")

    def sendmessage(self, text):
        self.updater.bot.send_message(chat_id=config.configdata["tgbot_userid"], text=text)


class WXpusher:
    def __init__(self):
        self.API_TOKEN = "AT_MrNwhC7N9jbt2hmdDXxOaGPkI7OmN8WV"
        self.baseurl = f"http://wxpusher.zjiecode.com/api/send/message/?appToken={self.API_TOKEN}\
        &uid={config.configdata['wxpusher_uid']}&content="

    def sendmessage(self, content):
        requests.get(f"{self.baseurl}{content}")


if config.tgbot_enable:
    tgbot = TGbot()

if config.wxpusher_enable:
    wxpusher = WXpusher()


def notification(content, error=False):
    info(content)
    if error:
        content = f"[ERROR] {content}"
    if config.tgbot_enable:
        tgbot.sendmessage(content)
    if config.wxpusher_enable:
        wxpusher.sendmessage(content)


def info(text):
    print(text)
    logging.info(text)


def error(text, time_hold=300):
    notification(text)
    logging.critical(text)
    driver.quit()
    time.sleep(time_hold)
    main()
    exit()


class User:
    def __init__(self):
        self.username = config.configdata["username"]
        self.password = config.configdata["password"]
        self.next_class = ""
        self.next_time = ""

    def login(self):
        try:
            driver.find_element("id", "username").send_keys(self.username)
            driver.find_element("id", "password").send_keys(self.password)
            driver.find_element("name", "submit").click()
        except BaseException:
            error("登录失败，可能是网站寄了，30分钟后重试", 1800)
            return False
        else:
            info("完成登录")
            return True

    def refresh(self):
        try:
            driver.get('https://my.manchester.ac.uk/MyCheckIn')
            time.sleep(5)
        except BaseException:
            error("网页加载失败，30分钟后重试", 1800)
            return False
        else:
            time.sleep(5)
            try:
                driver.find_element("class name", "c-button--logout")  # 检测登出按钮
                info("已登录，状态正常")
            except BaseException:
                info("登录失效，开始登陆")
                self.login()
            else:
                return True

    def checkin(self):
        self.refresh()
        time.sleep(5)
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()  # 尝试点击签到
            time.sleep(5)
        except BaseException:  # 没有按钮
            return
        else:
            self.refresh()
            try:
                driver.find_element("xpath", "//*[text()='Check-in successful']")  # 成功点击，检测是否已经成功
            except BaseException:
                error("签到失败，5分钟后重试", 300)
                return False
            notification("完成了一次签到")
            return True

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
    date = datetime.date.today().strftime("%Y/%m/%d").split("/")
    time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hh, mm, ss)
    time = config.tzlondon.localize(time)
    time = time.astimezone(config.tzlocal)
    return [time.strftime('%H:%M:%S'), f"{hh}:{mm}:{ss}"]  # 修正时区|伦敦时区


def job():
    setup_driver()
    user.checkin()
    schedule.clear()
    nexttime = user.getcheckintime()
    schedule.every().day.at(nexttime[0]).do(job)
    info(f"已设置下次执行时间（本地时区）：{nexttime[0]}")
    notification(f"已设置下次执行时间：{nexttime[1]}")
    driver.quit()


def main():
    notification("自动签到开始运行")
    global user
    user = User()
    job()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
