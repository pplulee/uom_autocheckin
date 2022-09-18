FROM python:slim-bullseye

WORKDIR /app
ADD main.py /app
ADD requirements.txt /app

RUN pip install -r requirements.txt

ENV webdriver=""
ENV username=""
ENV password=""
ENV tgbot_userid=""
ENV tgbot_token=""
ENV wxpusher_uid=""

CMD python -u /app/main.py --webdriver=$webdriver --username=$username --password=$password --tgbot_userid=$tgbot_userid --tgbot_token=$tgbot_token --wxpusher_uid=$wxpusher_uid
