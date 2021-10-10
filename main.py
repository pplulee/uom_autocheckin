from selenium import webdriver
import time
import schedule

opt = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=opt)


class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.isLogin = False

    def login(self):
        print("打开URL")
        driver.get('https://my.manchester.ac.uk/en/MyCheckIn')
        driver.find_element_by_id('userNameInput').send_keys(self.username)
        driver.find_element_by_id('nextButton').click()
        print("输入账号")
        driver.find_element_by_id('passwordInput').send_keys(self.password)
        driver.find_element_by_id('submitButton').click()
        print("输入密码")
        self.isLogin = True

    def refresh(self):
        driver.get('https://my.manchester.ac.uk/en/MyCheckIn')
        try:
            driver.find_element_by_class_name('s-logout-button-container')
        except BaseException:
            print("未登陆，开始登陆")
            self.login()
        else:
            print("已登录，状态正常")

    def signin(self):
        self.refresh()
        try:
            driver.find_element_by_class_name('s-logout-button-container')  # 检测登出按钮
        except BaseException:
            print("未检测到需要签到的项目")
            return False
        else:
            driver.find_element_by_id('').click()  # 还没抓


userobj = user("", "")
userobj.login()
#schedule.every().hour.at(":52").do(userobj.signin())
