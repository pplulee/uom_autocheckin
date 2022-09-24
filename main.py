import argparse
import datetime
import logging
import os.path
import time
from json import loads
from random import randint

import pytz
import schedule
from requests import get
from selenium import webdriver
from telegram.ext import Updater, CommandHandler
from tzlocal import get_localzone

parser = argparse.ArgumentParser(description="")
parser.add_argument("--config_path", default="")
parser.add_argument("--webdriver", default="local")
parser.add_argument("--username", default="")
parser.add_argument("--password", default="")
parser.add_argument("--tgbot_userid", default="")
parser.add_argument("--tgbot_token", default="")
parser.add_argument("--wxpusher_uid", default="")
parser.add_argument("--debug", default=False, action="store_true")
args = parser.parse_args()


class Config:
    def __init__(self):
        self.tgbot_enable = False
        self.wxpusher_enable = False
        self.isremote = False
        self.debug = args.debug
        if args.config_path != "" or os.path.exists("config.json"):  # 读取配置文件
            configfile = open("config.json" if args.config_path == "" else args.config_path, "r")
            self.configdata = loads(configfile.read())
            configfile.close()
            self.username = self.configdata["username"]
            self.password = self.configdata["password"]
            self.webdriver = self.configdata["webdriver"]
            if self.configdata["tgbot_enable"] == 1:
                self.tgbot_enable = True
                self.tgbot_userid = self.configdata["tgbot_userid"]
                self.tgbot_token = self.configdata["tgbot_token"]
            if self.configdata["wxpusher_enable"] == 1:
                self.wxpusher_enable = True
                self.wxpusher_uid = self.configdata["wxpusher_uid"]
        else:  # 从命令行参数读取
            self.webdriver = args.webdriver
            self.username = args.username
            self.password = args.password
            if args.tgbot_userid != "" and args.tgbot_token != "":
                self.tgbot_enable = True
                self.tgbot_userid = args.tgbot_userid
                self.tgbot_token = args.tgbot_token
            if args.wxpusher_uid != "":
                self.wxpusher_uid = args.wxpusher_uid
        if self.webdriver != "local":
            self.isremote = True
        if self.username == "" or self.password == "":
            print("用户名或密码为空")
            exit()
        if self.webdriver == "":
            print("webdriver为空")
            exit()
        self.tzlondon = pytz.timezone("Europe/London")  # Time zone
        self.tzlocal = get_localzone()


config = Config()


class TGbot:
    def __init__(self):
        self.updater = Updater(config.tgbot_token)
        self.updater.dispatcher.add_handler(CommandHandler('ping', self.ping))
        self.updater.dispatcher.add_handler(CommandHandler('nextclass', self.nextclass))
        self.updater.dispatcher.add_handler(CommandHandler('nexttime', self.nexttime))
        self.updater.start_polling()

    def ping(self, bot, update):
        info("Telegram 检测存活")
        self.sendmessage("还活着捏")

    def nextclass(self, bot, update):
        info("Telegram 下节课信息")
        self.sendmessage(f"下节课是：{user.next_class}")

    def nexttime(self, bot, update):
        info("Telegram 下节课时间")
        self.sendmessage(f"下节课的时间：{user.next_time}")

    def sendmessage(self, text):
        self.updater.bot.send_message(chat_id=config.tgbot_userid, text=text)


class WXpusher:
    def __init__(self):
        self.API_TOKEN = "AT_MrNwhC7N9jbt2hmdDXxOaGPkI7OmN8WV"
        self.baseurl = f"http://wxpusher.zjiecode.com/api/send/message/?appToken={self.API_TOKEN}\
        &uid={config.wxpusher_uid}&content="

    def sendmessage(self, content):
        get(f"{self.baseurl}{content}")


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


def setup_driver():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('ignore-certificate-errors')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/101.0.4951.54 Safari/537.36")
    try:
        if config.isremote:
            driver = webdriver.Remote(command_executor=config.webdriver, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    except BaseException as e:
        print(e)
        error("Webdriver调用失败")
    else:
        driver.set_page_load_timeout(15)


class User:
    def __init__(self):
        self.username = config.username
        self.password = config.password
        self.next_class = "未获取"
        self.next_time = "未获取"

    def check_login(self):
        self.refresh()
        try:
            driver.find_element("class name", "c-button--logout")  # 检测登出按钮
        except BaseException:
            return False  # 未找到登出按钮
        else:
            return True  # 找到登出按钮

    def login(self):
        login_count = 0
        while not (self.check_login()):
            login_count += 1
            if login_count > 3:
                notification("登陆失败次数过多，退出程序")
                exit()
            info(f"开始第{login_count}次登录")
            try:
                driver.find_element("id", "username").send_keys(self.username)
                driver.find_element("id", "password").send_keys(self.password)
                driver.find_element("name", "submit").click()
            except BaseException as e:
                print(e)
                error("登录失败，可能是网站寄了，30分钟后重试", 1800)
                return False
            else:
                try:
                    driver.find_element("xpath", "//*[@id='msg']")
                except BaseException:
                    pass
                else:
                    notification("用户名或密码错误，退出程序")
                    exit()
        return True

    def refresh(self, retry=0):
        if retry > 3:
            error("网页加载失败3次，30分钟后重试", 1800)
            return False
        try:
            driver.get('https://my.manchester.ac.uk/MyCheckIn')
            time.sleep(5)
        except BaseException as e:
            print(e)
            self.refresh(retry + 1)
            return False
        else:
            return True

    def checkin(self):
        self.login()
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()  # 尝试点击签到
            time.sleep(3)
        except BaseException:  # 没有可签到项目
            return
        else:
            self.refresh()
            try:
                driver.find_element("xpath", "//*[text()='Check-in successful']")  # 成功点击，检测是否已经成功
            except BaseException as e:
                print(e)
                error("签到失败，5分钟后重试", 300)
                return False
            notification("完成了一次签到")
            return True

    def getcheckintime(self):
        self.refresh()
        try:
            content = driver.find_element("xpath", "//*[contains(text(),'Check-in open at ')]").text
        except BaseException:
            notification("已完成当天所有签到\n自动设置下一天运行")
            schedule.clear()
            self.next_class = "未获取"
            return modifytime(6, 0, 0)
        else:
            try:
                driver.find_element("xpath", "//*[text()='Check-in successful']")
            except BaseException:
                # 第一个项目未签到
                self.next_class = driver.find_elements("class name", "u-font-bold")[2].text
            else:
                # 第一个项目已签到，抓取下一个项目的时间
                self.next_class = driver.find_elements("class name", "u-font-bold")[3].text
            self.next_time = randomtime(content[-5:])  # 首个任务的时间
            notification(f"下一节课是{self.next_class}\n签到时间{self.next_time[1]}")
            return self.next_time


def randomtime(time):  # 随机时间
    return modifytime(int(time[:2]), int(time[3:]) + randint(0, 8), randint(0, 59))


def modifytime(hh, mm, ss):  # 换算时区
    date = datetime.date.today().strftime("%Y/%m/%d").split("/")
    time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hh, mm, ss)
    time = config.tzlondon.localize(time)
    time = time.astimezone(config.tzlocal)
    return [time.strftime('%H:%M:%S'), f"{hh}:{mm}:{ss}"]  # 修正时区|伦敦时区


def job():
    if (datetime.datetime.today().isoweekday() == 6 or 7) and not config.debug:
        # 周末不运行，设置下一天
        print("今天是周末，不运行")
        schedule.clear()
        nexttime = modifytime(randint(5, 7), randint(0, 59), randint(0, 59))
        schedule.every().day.at(nexttime[0]).do(job)
        print(f"已设置下次执行时间（本地时区）：{nexttime[0]}")
    else:
        setup_driver()
        user.checkin()
        schedule.clear()
        nexttime = user.getcheckintime()
        schedule.every().day.at(nexttime[0]).do(job)
        info(f"已设置下次执行时间（本地时区）：{nexttime[0]}")
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
