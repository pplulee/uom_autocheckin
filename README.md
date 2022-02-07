# UoM 自动签到
> 请注意目前本程序仅支持中文输出

[Click Here for English Version](README_en.md)

[日本語のバッションはこちらへ](README_jp.md)

## 这是什么？
懂得都懂，不懂的说了也不懂，你也别问，利益牵扯太大，说了对你们没好处，我只能说水很深

## 如何使用
clone后，需先安装pip依赖
```pip install -r requirements.txt```

然后修改```config.json```内参数，再运行```main.py```即可
* 若选择本机运行，```webdriver```处填写```local```，并确保安装了对应版本的[ChromeDriver](https://chromedriver.chromium.org/downloads)
* 若使用远程webdriver，```webdriver```处填写地址。推荐配合[Docker - browserless/chrome](https://registry.hub.docker.com/r/browserless/chrome) 使用

强烈推荐使用远程webdriver

程序可以自动识别时差并自动调整，无须担心时差问题

完成当天所有签到任务后，会设置一条次日0时的定时任务，在次日继续运行

## 常见问题
* 如果网站寄了，程序也会直接寄