import argparse
import logging
import os.path
import random
import re
import time
from json import loads

import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from ActivityType import ActivityType
from FormLink import FormLink
from School import School

formlink = FormLink()

cancel_flag = False

parser = argparse.ArgumentParser(description="")
parser.add_argument("--config_path", default="")
parser.add_argument("--webdriver", default="local")
parser.add_argument("--studentID", default="")
parser.add_argument("--email", default="")
parser.add_argument("--username", default="")
parser.add_argument("--password", default="")
parser.add_argument("--school", default="")
parser.add_argument("--tgbot_chat_id", default="")
parser.add_argument("--tgbot_token", default="")
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
        self.isremote = False
        if args.config_path != "" or os.path.exists("config.json"):  # 读取配置文件
            configfile = open("config.json" if args.config_path == "" else args.config_path, "r")
            self.configdata = loads(configfile.read())
            configfile.close()
            self.studentID = self.configdata["studentID"]
            self.email = self.configdata["email"]
            self.username = self.configdata["username"]
            self.password = self.configdata["password"]
            self.school = self.configdata["school"]
            self.webdriver = self.configdata["webdriver"]
            self.debug = self.configdata["debug"] == 1
            self.tgbot_chat_id = self.configdata["tgbot_chat_id"]
            self.tgbot_token = self.configdata["tgbot_token"]
        else:  # 从命令行参数读取
            self.webdriver = args.webdriver
            self.studentID = args.studentID
            self.email = args.email
            self.username = args.username
            self.password = args.password
            self.school = args.school
            self.debug = args.debug
            self.tgbot_chat_id = args.tgbot_chat_id
            self.tgbot_token = args.tgbot_token
        self.isremote = self.webdriver != "local"
        if self.email == "":
            logger.error("邮箱为空")
            exit()
        if self.username == "":
            logger.error("用户名为空")
            exit()
        if self.password == "":
            logger.error("密码为空")
            exit()
        if self.studentID == "":
            logger.error("学生ID为空")
            exit()
        if self.school == "":
            logger.error("学院为空")
            exit()
        if self.webdriver == "":
            logger.error("webdriver为空")
            exit()


config = Config()
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


@tgbot.message_handler(commands=['schools'])
def bot_ping(message):
    if check_chat_id(message):
        tgbot.reply_to(message, '可用学院：\n' + '\n'.join(School.xpath.keys()))


@tgbot.message_handler(commands=['activities'])
def bot_ping(message):
    if check_chat_id(message):
        tgbot.reply_to(message, '可用活动类型：\n' + '\n'.join(ActivityType.xpath.keys()))


@tgbot.message_handler(commands=['fill'])
def bot_job(message):
    global cancel_flag
    cancel_flag = False
    if check_chat_id(message):
        logger.info("开始执行填表任务")
        url = formlink.get_link()
        if url is None:
            notification("未找到对应的表单链接", True)
            return
        text = message.text
        # <unit> <type>
        match = re.match(r'/fill (\S+) (\S+)', text)
        if not match:
            tgbot.reply_to(message, "格式有误，请使用 /fill <unit> <type>")
            return
        unit = match.group(1)
        fill_type = match.group(2)
        reply = tgbot.reply_to(message, "开始执行填表任务……")
        webdriver_result = setup_driver()
        if not webdriver_result:
            notification("webdriver调用失败", True)
        else:
            login_result = user.login()
            if login_result:
                if user.fillform(unit=unit, type=fill_type, submit=True):
                    tgbot.edit_message_text(chat_id=reply.chat.id, message_id=reply.message_id, text="填表成功")
                else:
                    tgbot.edit_message_text(chat_id=reply.chat.id, message_id=reply.message_id, text="填表失败")
        try:
            driver.quit()
        except BaseException:
            pass
        cancel_flag = False


@tgbot.message_handler(commands=['testlogin'])
def bot_testlogin(message):
    if check_chat_id(message):
        reply = tgbot.reply_to(message, "开始测试登录……")
        url = formlink.get_link()
        if url is None:
            notification("未找到对应的表单链接", True)
            return
        result = user.test_login()
        if result:
            tgbot.edit_message_text(chat_id=reply.chat.id, message_id=reply.message_id, text="测试登录成功")
        else:
            tgbot.edit_message_text(chat_id=reply.chat.id, message_id=reply.message_id, text="测试登录失败")


@tgbot.message_handler(commands=['getlog'])
def bot_getlog(message):
    if check_chat_id(message):
        logger.info("Telegram 发送日志")
        tgbot.send_document(chat_id=config.tgbot_chat_id, document=open('log.txt', 'rb'))


@tgbot.message_handler(commands=['cancel'])
def bot_cancel(message):
    global cancel_flag
    if check_chat_id(message):
        logger.info("停止当前任务")
        cancel_flag = True
        driver.quit()


def bot_send_photo():
    record_screen()
    tgbot.send_photo(chat_id=config.tgbot_chat_id, photo=open('save.png', 'rb'))


def bot_start_polling():
    tgbot.infinity_polling(skip_pending=True, timeout=10)


def record_screen():
    try:
        # 保存页面到文件
        with open("save.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        # 保存页面截图到文件
        driver.save_screenshot("save.png")
    except BaseException:
        logger.error("保存截图失败")
    else:
        logger.info("保存截图成功")


def notification(content, error=False):
    logger.info(content) if not error else logger.error(content)
    if error:
        content = f"错误：{content}"
    bot_send_message(content)


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
        self.studentID = config.studentID
        self.email = config.email
        self.username = config.username
        self.password = config.password
        self.school = config.school

    def refresh(self, retry=0):
        global cancel_flag
        if cancel_flag:
            return False
        if retry > 3:
            notification("网页加载失败3次", True)
            return False
        try:
            driver.get(formlink.get_link())
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "loginfmt")))
        except BaseException as e:
            logger.error("页面加载失败，自动重试")
            logger.error(e)
            return self.refresh(retry + 1)
        else:
            return True

    def login(self, retry=0):
        global cancel_flag
        if cancel_flag:
            return False
        if retry > 3:
            notification("登录失败3次，自动退出", True)
            return False
        if not self.refresh():
            notification("网页加载失败，自动退出", True)
            return False
        try:
            driver.find_element(By.NAME, "loginfmt").send_keys(self.email)
            driver.find_element(By.ID, "idSIButton9").click()
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(
                self.username)
            driver.find_element(By.ID, "password").send_keys(self.password)
            time.sleep(1)
            driver.find_element(By.NAME, "submit").click()
        except BaseException as e:
            logger.error("登陆失败，自动重试")
            logger.error(e)
            return self.login(retry + 1)

        # 处理DUO
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "duo_iframe")))
        except BaseException as e:
            bot_send_photo()
            notification("DUO验证失败", True)
            return False
        else:
            notification("请在手机上完成二步验证")
        # 等待完成验证
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id=\"question-list\"]/div[1]/div[2]/div/span/input")))
        except BaseException as e:
            bot_send_photo()
            notification("DUO验证失败", True)
            return False
        else:
            logger.info("登录成功")
            return True

    def fillform(self, unit, type, submit=False):
        global cancel_flag
        if cancel_flag:
            return False
        try:
            # Student ID
            driver.find_element(By.XPATH, "//*[@id=\"question-list\"]/div[1]/div[2]/div/span/input").send_keys(
                self.studentID)

            # School
            driver.find_element(By.XPATH, "//*[@id=\"question-list\"]/div[2]/div[2]/div/div/div").click()
            driver.find_element(By.XPATH, School.xpath[self.school]).click()
            if self.school == "Other":
                driver.find_element(By.XPATH, "//*[@id=\"question-list\"]/div[2]/div[2]/div/span/input").send_keys(
                    self.school)

            # Unit
            driver.find_element(By.XPATH, "//*[@id=\"question-list\"]/div[3]/div[2]/div/span/input").send_keys(unit)

            # Activity Type
            driver.find_element(By.XPATH, "//*[@id=\"question-list\"]/div[4]/div[2]/div/div/div").click()
            driver.find_element(By.XPATH, ActivityType.xpath[type]).click()
            if type == "Other":
                driver.find_element(By.XPATH, "//*[@id=\"question-list\"]/div[4]/div[2]/div/span/input").send_keys(type)

            driver.find_element(By.XPATH,
                                "//*[@id=\"question-list\"]/div[5]/div[2]/div/div/div/div/label/span[1]/input").click()
            time.sleep(1)
            # 提交
            if submit:
                driver.find_element(By.XPATH,
                                    "//*[@id=\"form-main-content1\"]/div/div/div[2]/div[3]/div/button").click()

        except BaseException as e:
            notification("填表失败", True)
            logger.error(e)
            bot_send_photo()
            return False
        else:
            notification("填表成功")
            bot_send_photo()
            return True

    def test_login(self):
        logger.info("测试登录")
        setup_driver()
        result = user.login()
        if result:
            fillresult = user.fillform(unit="test", type=random.choice(list(ActivityType.xpath.keys())), submit=False)
            try:
                driver.quit()
            except BaseException:
                pass
            if fillresult:
                return False
            else:
                return False
        else:
            return False


def main():
    notification(
        "自动签到开始运行\n欢迎关注官方Telegram频道\nt.me/uom_autocheckin\n以获取最新通知\n！使用前请确保已设置默认二步验证推送设备！")
    global user
    user = User()
    tgbot.infinity_polling(skip_pending=True, timeout=10)


if __name__ == '__main__':
    main()
