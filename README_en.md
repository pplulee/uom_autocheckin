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

After completing all check-ins in present day, a scheduled task will be automatically set to 12:00AM in the next day, so 
that the program can continue execution afterwards.

~~English Version Translator: Tenjin~~