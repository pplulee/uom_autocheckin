import argparse
import datetime
import logging
import os.path
import random
import threading
import time
from json import loads
from random import randint

import pytz
import schedule
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tzlocal import get_localzone

from WXpusher import WXpusher

parser = argparse.ArgumentParser(description="")
parser.add_argument("--config_path", default="")
parser.add_argument("--webdriver", default="local")
parser.add_argument("--username", default="")
parser.add_argument("--password", default="")
parser.add_argument("--tgbot_chat_id", default="")
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
fhlr = logging.FileHandler('log.txt', mode='w')  # 输出到文件的handler
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
                self.tgbot_chat_id = self.configdata["tgbot_chat_id"]
                self.tgbot_token = self.configdata["tgbot_token"]
            if self.configdata["wxpusher_enable"] == 1:
                self.wxpusher_enable = True
                self.wxpusher_uid = self.configdata["wxpusher_uid"]
        else:  # 从命令行参数读取
            self.webdriver = args.webdriver
            self.username = args.username
            self.password = args.password
            self.debug = args.debug
            if args.tgbot_chat_id != "" and args.tgbot_token != "":
                self.tgbot_enable = True
                self.tgbot_chat_id = args.tgbot_chat_id
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

if config.tgbot_enable:
    tgbot = telebot.TeleBot(config.tgbot_token)


    def check_chat_id(message):
        if str(message.chat.id) == config.tgbot_chat_id:
            return True
        else:
            tgbot.reply_to(message, "你没有权限使用此命令")
            return False


    def bot_send_message(content):
        tgbot.send_message(chat_id=config.tgbot_chat_id, text=content)


    @tgbot.message_handler(commands=['start', 'ping'])
    def bot_ping(message):
        if check_chat_id(message):
            tgbot.reply_to(message, '还活着捏')


    @tgbot.message_handler(commands=['nextclass'])
    def bot_nextclass(message):
        if check_chat_id(message):
            tgbot.reply_to(message, f"下节课是：{user.next_class}")


    @tgbot.message_handler(commands=['nexttime'])
    def bot_nexttime(message):
        if check_chat_id(message):
            tgbot.reply_to(message, f"下节课的时间：{user.next_time}")


    @tgbot.message_handler(commands=['job'])
    def bot_job(message):
        if check_chat_id(message):
            logger.info("手动执行任务")
            tgbot.reply_to(message, "已发送请求")
            job()


    @tgbot.message_handler(commands=['getlog'])
    def bot_getlog(message):
        if check_chat_id(message):
            logger.info("Telegram 发送日志")
            tgbot.send_document(chat_id=config.tgbot_chat_id, document=open('log.txt', 'rb'))


    @tgbot.message_handler(commands=['checkwebsite'])
    def check_website(message):
        if check_chat_id(message):
            logger.info("执行检测学校网站")
            reply = tgbot.reply_to(message, "正在检测网站……")
            setup_driver()
            tgbot.edit_message_text(chat_id=config.tgbot_chat_id, message_id=reply.message_id,
                                    text="网站正常" if user.refresh() else "网站异常")
            driver.quit()


    def bot_start_polling():
        tgbot.infinity_polling(skip_pending=True, timeout=10)


    thread_bot = threading.Thread(target=bot_start_polling, daemon=True)
    thread_bot.start()

if config.wxpusher_enable:
    wxpusher = WXpusher(config.wxpusher_uid)


def notification(content, error=False):
    logger.info(content) if not error else logger.error(content)
    if error:
        content = f"错误：{content}"
    if config.tgbot_enable:
        bot_send_message(content)
    if config.wxpusher_enable:
        wxpusher.send_message(content)


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
    if not config.debug:
        options.add_argument("--headless")
    user_agents = [
        # Windows Chrome
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        # macOS Chrome
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        # Linux Chrome
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
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
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.CLASS_NAME, "c-button--logout")))  # 检测登出按钮
        except BaseException:
            pass  # 未登录
        else:
            return True, "已登录"  # 找到登出按钮
        logger.info(f"开始第{retry}次登录")
        try:
            driver.find_element(By.ID, "username").send_keys(self.username)
            driver.find_element(By.ID, "password").send_keys(self.password)
            time.sleep(1)
            driver.find_element(By.NAME, "submit").click()
        except BaseException as e:
            logger.error("登陆失败，自动重试")
            logger.error(e)
            return self.login(retry + 1)
        else:
            try:
                driver.find_element(By.XPATH, "//*[@id='msg']")
            except BaseException:
                pass
            else:
                notification("用户名或密码错误，退出程序", True)
                driver.quit()
                exit()
        WebDriverWait(driver, 5).until_not(EC.presence_of_element_located((By.NAME, "submit")))  # 等待登录按钮消失
        logger.info("登录成功")
        return True, "登陆成功"

    def checkin(self):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "StudentSelfCheckinSubmit"))).click()  # 等待签到成功
        except BaseException:  # 没有可签到项目
            logger.info("没有可签到项目")
            return True, "没有可签到项目"
        else:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[text()='Check-in successful']")))  # 成功点击，检测是否已经成功
            except BaseException as e:
                logger.error("签到执行失败")
                logger.error(e)
                return False, "签到失败"
            else:
                notification("完成了一次签到")
                return True, "签到成功"

    def getcheckintime(self):
        try:
            content = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Check-in open at ')]"))).text
        except BaseException:
            self.next_class = "未获取"
            return None
        else:
            try:
                driver.find_element(By.XPATH, "//*[text()='Check-in successful']")
            except BaseException:
                # 第一个项目未签到
                self.next_class = driver.find_elements(By.CLASS_NAME, "u-font-bold")[2].text
            else:
                # 第一个项目已签到，抓取下一个项目的时间
                self.next_class = driver.find_elements(By.CLASS_NAME, "u-font-bold")[3].text
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
        logger.info(f"下次签到时间：{nexttime[1]}")
        schedule.every().day.at(nexttime[0]).do(job).tag("checkin_task")  # 随机时间执行首次任务


def job():
    logger.info("开始执行签到任务")
    schedule.clear("checkin_task")
    webdriver_result = setup_driver()
    next_time = None
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
                else:
                    notification(f"下一节课是：{user.next_class}\n签到时间：{checkin_time[1]}")
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
