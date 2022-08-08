# UoM Auto check-in
> Please be aware that this program currently only support Chinese output display

[中文版在这](README.md)

[日本語のバッションはこちらへ](README_jp.md)

## What's this
You know the rules, and so do I~ If you don't know, never ask. It's DEEEEEEEEEEP~

## How to use
1. clone the files
2. install Python dependants by using pip command

```pip install -r requirements.txt```

3. modify the parameters in ```config.json```, finally run```main.py```
* To run locally, use```local```after```"webdriver":```Make sure you have installed the correspondent version of [ChromeDriver](https://chromedriver.chromium.org/downloads)
* To use remote webdriver, append your address after```"webdriver":```
[Docker - browserless/chrome](https://registry.hub.docker.com/r/browserless/chrome) is recommended

STRONGLY RECOMMEND TO USE REMOTE WEBDRIVER

The program is optimized to analyse time difference and adjust itself, no need to change manually

After completing all check-ins in present day, a scheduled task will be automatically set to 6:00AM in the next day, so 
that the program can continue execution afterwards.

## Docker Method(x86_64 and arm64V8 are tested)
### 1.Use Docker Hub
* Use `docker pull sahuidhsu/uom_autocheckin` to download the latest version of the image(ARM64 users please use `sahuidhsu/uom_autocheckin:arm64` instead)
* Run `docker run -d --name=uom_checkin -e xxx=xxx -e xxx=xxx -e xxx=xxx... sahuidhsu/uom_autocheckin`(ARM64 users please add `:arm64` at the end), here the`xxx=xxx`is
in the format of config.json. e.g. `-e username=u11451hh -e password=123456 -e webdriver=local -e tgbot_token=xxx...`


### 2.Use Dockerfile locally
* Clone this repository, then run `docker build -t uom_checkin .` inside root path(be aware of the last dot!)
* Run `docker run -d --name=uom_checkin -e xxx=xxx -e xxx=xxx -e xxx=xxx... uom_checkin`, here the`xxx=xxx`is
in the format of config.json. e.g. `-e username=u11451hh -e password=123456 -e webdriver=local -e tgbot_token=xxx...`


### Log function is not yet supported for Docker methods, so please use the push function to send the result to your telegram bot or WeChat

English Version Translator: [LTY_CK_TS](https://github.com/sahuidhsu)