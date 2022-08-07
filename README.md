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
* 若使用远程webdriver，```webdriver```
  处填写地址。推荐配合[Docker - browserless/chrome](https://registry.hub.docker.com/r/browserless/chrome) 使用

强烈推荐使用远程webdriver

程序可以自动识别时差并自动调整，无须担心时差问题

完成当天所有签到任务后，会设置一条次日6时的定时任务，在次日继续运行

程序提供了 ```--config_path``` 的启动参数（可选），可以指定配置文件路径。如果不指定，则默认查找```config.json```

## Docker运行方法(已测试支持x86_64与arm64v8)
* 安装Docker
* 将本项目克隆到本地
* 在项目根目录执行`docker build -t uom_checkin .`命令(注意后面有个英文句号)
* 使用`docker run -d --name=uom_checkin -e xxx=xxx -e xxx=xxx -e xxx=xxx... uom_checkin`命令启动项目 此处的`xxx=xxx`按
config.json中的配置填写即可，如 `-e username=u11451hh -e password=123456 -e webdriver=local -e tgbot_token=xxx...`
* 目前暂不支持查看日志，请配置推送以查看签到结果