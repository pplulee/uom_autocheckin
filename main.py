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
        self.updater.dispatcher.add_handler(CommandHandler('job', self.job))
        self.updater.dispatcher.add_handler(CommandHandler('checkwebsite', self.check_website))
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

    def job(self, bot, update):
        info("手动执行任务")
        self.sendmessage("已发送请求")
        job()

    def check_website(self, bot, update):
        info("执行检测学校网站")
        setup_driver()
        result = user.refresh()
        if result:
            self.sendmessage("网站正常")
        else:
            self.sendmessage("网站异常")
        driver.quit()

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
    notification(text, True)
    logging.critical(text)
    driver.quit()
    schedule.clear("checkin_task")
    next_time = (datetime.datetime.now() + datetime.timedelta(seconds=time_hold)).strftime("%H:%M:%S")
    schedule.every().day.at(next_time).do(job).tag("checkin_task")


def setup_driver():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
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
        try:
            driver.find_element("class name", "c-button--logout")  # 检测登出按钮
        except BaseException:
            return False  # 未找到登出按钮
        else:
            return True  # 找到登出按钮

    def login(self, retry=0):
        retry += 1
        if retry > 3:
            return False, "登陆失败3次"
        if not self.refresh():
            return False, "登陆失败，页面加载失败"
        if not self.check_login():
            info(f"开始第{retry}次登录")
            try:
                driver.find_element("id", "username").send_keys(self.username)
                driver.find_element("id", "password").send_keys(self.password)
                driver.find_element("name", "submit").click()
            except BaseException as e:
                print("登陆失败，自动重试")
                print(e)
                return self.login(retry)
            else:
                try:
                    driver.find_element("xpath", "//*[@id='msg']")
                except BaseException:
                    pass
                else:
                    notification("用户名或密码错误，退出程序")
                    exit()
        return True, "登陆成功"

    def refresh(self, retry=0):
        retry += 1
        if retry > 3:
            print("网页加载失败3次")
            return False
        try:
            driver.get('https://my.manchester.ac.uk/MyCheckIn')
            time.sleep(3)
        except BaseException as e:
            print("页面加载失败，自动重试")
            print(e)
            return self.refresh(retry)
        else:
            return True

    def checkin(self):
        if not self.refresh():
            return False, "签到失败，页面加载失败"
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()  # 尝试点击签到
        except BaseException:  # 没有可签到项目
            return True, "已签到"
        else:
            try:
                driver.find_element("xpath", "//*[text()='Check-in successful']")  # 成功点击，检测是否已经成功
            except BaseException as e:
                print("签到失败")
                print(e)
                return False, "签到失败"
            else:
                notification("完成了一次签到")
                return True, "签到成功"

    def getcheckintime(self):
        self.login()
        try:
            content = driver.find_element("xpath", "//*[contains(text(),'Check-in open at ')]").text
        except BaseException:
            self.next_class = "未获取"
            return None
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
            return self.next_time


def randomtime(time):  # 随机时间
    return modifytime(int(time[:2]), int(time[3:]) + randint(0, 8), randint(0, 59))


def modifytime(hh, mm, ss):  # 换算时区
    date = datetime.date.today().strftime("%Y/%m/%d").split("/")
    time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hh, mm, ss)
    time = config.tzlondon.localize(time)
    time = time.astimezone(config.tzlocal)
    return [time.strftime('%H:%M:%S'), f"{hh}:{mm}:{ss}"]  # 修正时区|伦敦时区


def dailycheck():
    if (datetime.datetime.today().isoweekday() in [6, 7]) and not config.debug:
        # 周末不运行，设置下一天
        print("今天是周末，不运行")
    else:
        if not schedule.get_jobs("checkin_task"):
            job()
        else:
            print("检测到任务已存在，不再重复添加")


def job():
    schedule.clear("checkin_task")
    setup_driver()
    login_result = user.login()
    if not login_result[0]:
        error(f"{login_result[1]}，15分钟后重试", 900)
        return
    checkin_result = user.checkin()
    if not checkin_result[0]:
        error(f"{checkin_result[1]}，15分钟后重试", 900)
        return
    nexttime = user.getcheckintime()
    if not (nexttime is None):
        schedule.every().day.at(nexttime[0]).do(job).tag("checkin_task")
        notification(f"下一节课是{user.next_class}\n签到时间{nexttime[1]}")
    else:
        notification("今天已完成所有签到")
    driver.quit()


def main():
    notification("自动签到开始运行")
    schedule.clear()
    dailytime = modifytime(randint(4, 7), randint(0, 59), randint(0, 59))
    schedule.every().day.at(dailytime[0]).do(dailycheck).tag("dailyjob")
    notification(f"已设置每日初始时间：{dailytime[1]}")
    global user
    user = User()
    dailycheck()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
