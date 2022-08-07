FROM python:3.8.2

ADD . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENV webdriver=""
ENV username=""
ENV password=""
ENV tgbot_userid=""
ENV tgbot_token=""
ENV wxpusher_uid=""

CMD python /app/main.py --webdriver=$webdriver --username=$username --password=$password --tgbot_userid=$tgbot_userid --tgbot_token=$tgbot_token --wxpusher_uid=$wxpusher_uid