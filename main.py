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

logger = logging.getLogger()
logger.setLevel('INFO')
BASIC_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler()  # 输出到控制台的handler
chlr.setFormatter(formatter)
fhlr = logging.FileHandler('log', mode='w')  # 输出到文件的handler
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)


class Config:
    def __init__(self):
        self.tgbot_enable = False
        self.wxpusher_enable = False
        self.isremote = False
        if args.config_path != "" or os.path.exists("config.json"):  # 读取配置文件
            configfile = open("config.json" if args.config_path == "" else args.config_path, "r")
            self.configdata = loads(configfile.read())
            configfile.close()
            self.username = self.configdata["username"]
            self.password = self.configdata["password"]
            self.webdriver = self.configdata["webdriver"]
            self.debug = self.configdata["debug"] == 1
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
            self.debug = args.debug
            if args.tgbot_userid != "" and args.tgbot_token != "":
                self.tgbot_enable = True
                self.tgbot_userid = args.tgbot_userid
                self.tgbot_token = args.tgbot_token
            if args.wxpusher_uid != "":
                self.wxpusher_enable = True
                self.wxpusher_uid = args.wxpusher_uid
        self.isremote = self.webdriver != "local"
        if self.username == "" or self.password == "":
            logger.error("用户名或密码为空")
            exit()
        if self.webdriver == "":
            logger.error("webdriver为空")
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
        self.updater.dispatcher.add_handler(CommandHandler('getlog', self.sendlogfile))
        self.updater.start_polling()

    def ping(self, bot, update):
        logger.info("Telegram 检测存活")
        self.sendmessage("还活着捏")

    def nextclass(self, bot, update):
        logger.info("Telegram 下节课信息")
        self.sendmessage(f"下节课是：{user.next_class}")

    def nexttime(self, bot, update):
        logger.info("Telegram 下节课时间")
        self.sendmessage(f"下节课的时间：{user.next_time}")

    def job(self, bot, update):
        logger.info("手动执行任务")
        self.sendmessage("已发送请求")
        job()

    def sendlogfile(self, bot, update):
        logger.info("Telegram 发送日志")
        self.updater.bot.send_document(chat_id=config.tgbot_userid, document=open('log', 'rb'))

    def check_website(self, bot, update):
        logger.info("执行检测学校网站")
        messageID = self.sendmessage("正在检测网站……")
        setup_driver()
        self.updater.dispatcher.bot.edit_message_text(chat_id=config.tgbot_userid, message_id=messageID,
                                                      text="网站正常" if user.refresh() else "网站异常")
        driver.quit()

    def sendmessage(self, text):
        return self.updater.bot.send_message(chat_id=config.tgbot_userid, text=text)["message_id"]


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
    logger.info(content) if not error else logger.error(content)
    if error:
        content = f"错误：{content}"
    if config.tgbot_enable:
        tgbot.sendmessage(content)
    if config.wxpusher_enable:
        wxpusher.sendmessage(content)


def setup_driver():
    global driver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("enable-automation")
    options.add_argument("--disable-extensions")
    options.add_argument("start-maximized")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/109.0.5414.83 Mobile/15E148 Safari/604.1")
    try:
        driver = webdriver.Remote(command_executor=config.webdriver,
                                  options=options) if config.isremote else webdriver.Chrome(options=options)
    except BaseException as e:
        logger.error("Webdriver调用失败")
        logger.error(e)
        return False
    else:
        driver.set_page_load_timeout(30)
        return True


class User:
    def __init__(self):
        self.username = config.username
        self.password = config.password
        self.next_class = "未获取"
        self.next_time = "未获取"

    def refresh(self, retry=0):
        if retry > 3:
            notification("网页加载失败3次", True)
            return False
        try:
            driver.get('https://my.manchester.ac.uk/MyCheckIn')
            time.sleep(5)
        except BaseException as e:
            logger.error("页面加载失败，自动重试")
            logger.error(e)
            return self.refresh(retry + 1)
        else:
            return True

    def login(self, retry=0):
        if retry > 3:
            logger.error("登录失败3次")
            return False, "登陆失败3次"
        if not self.refresh():
            logger.error("登录失败，网页加载失败")
            return False, "登陆失败，网页加载失败"

        try:
            driver.find_element("class name", "c-button--logout")  # 检测登出按钮
        except BaseException:
            pass  # 未找到登出按钮
        else:
            return True, "已登录"  # 找到登出按钮

        logger.info(f"开始第{retry}次登录")
        try:
            driver.find_element("id", "username").send_keys(self.username)
            driver.find_element("id", "password").send_keys(self.password)
            driver.find_element("name", "submit").click()
        except BaseException as e:
            logger.error("登陆失败，自动重试")
            logger.error(e)
            return self.login(retry)
        else:
            try:
                driver.find_element("xpath", "//*[@id='msg']")
            except BaseException:
                pass
            else:
                notification("用户名或密码错误，退出程序", True)
                driver.quit()
                exit()
        logger.info("登录成功")
        return True, "登陆成功"

    def checkin(self):
        try:
            driver.find_element("name", "StudentSelfCheckinSubmit").click()  # 尝试点击签到
        except BaseException:  # 没有可签到项目
            logger.info("没有可签到项目")
            return True, "没有可签到项目"
        else:
            try:
                driver.find_element("xpath", "//*[text()='Check-in successful']")  # 成功点击，检测是否已经成功
            except BaseException as e:
                logger.error("签到执行失败")
                logger.error(e)
                return False, "签到失败"
            else:
                notification("完成了一次签到")
                return True, "签到成功"

    def getcheckintime(self):
        login_result = self.login()
        if not login_result[0]:
            return False, login_result[1]
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
    return modifytime(int(time[:2]), int(time[3:]) + randint(0, 7), randint(0, 59))


def modifytime(hh, mm, ss):  # 换算时区
    date = datetime.date.today().strftime("%Y/%m/%d").split("/")
    time = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hh, mm, ss)
    time = config.tzlondon.localize(time)
    time = time.astimezone(config.tzlocal)
    return [time.strftime('%H:%M:%S'), f"{hh}:{mm}:{ss}"]  # 修正时区|伦敦时区


def dailycheck():
    logger.info("开始执行每日任务")
    if (datetime.datetime.today().isoweekday() in [6, 7]) and not config.debug:
        # 周末不运行，设置下一天
        logger.info("今天是周末，不运行")
    else:
        schedule.clear("checkin_task")
        nexttime = modifytime(randint(4, 7), randint(0, 59), randint(0, 59))
        schedule.every().day.at(nexttime[0]).do(job).tag("checkin_task")  # 随机时间执行首次任务


def job():
    logger.info("开始执行签到任务")
    schedule.clear("checkin_task")
    webdriver_result = setup_driver()
    if not webdriver_result:
        notification("webdriver调用失败，15分钟后重试", True)
        next_time = (datetime.datetime.now() + datetime.timedelta(seconds=900)).strftime("%H:%M:%S")
    else:
        login_result = user.login()
        if not login_result[0]:
            notification(f"{login_result[1]}，15分钟后重试", True)
            next_time = (datetime.datetime.now() + datetime.timedelta(seconds=900)).strftime("%H:%M:%S")
        else:
            checkin_result = user.checkin()
            if not checkin_result[0]:
                notification(f"{checkin_result[1]}，15分钟后重试", True)
                next_time = (datetime.datetime.now() + datetime.timedelta(seconds=900)).strftime("%H:%M:%S")
            else:
                checkin_time = user.getcheckintime()
                if checkin_time is None:
                    notification("今天已完成所有签到，将在次日自动运行")
                    next_time = None
                else:
                    notification(f"下一节课是{user.next_class}\n签到时间{checkin_time[1]}")
                    next_time = checkin_time[0]
    if next_time is not None:
        schedule.every().day.at(next_time).do(job).tag("checkin_task")
    try:
        driver.quit()
    except BaseException:
        pass


def main():
    notification("自动签到开始运行\n欢迎关注官方Telegram频道\nt.me/uom_autocheckin\n以获取最新通知")
    schedule.clear()
    schedule.every().day.at(modifytime(1, 0, 0)[0]).do(dailycheck).tag("dailyjob")
    global user
    user = User()
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
