FROM python:3.9-slim

WORKDIR /app
ADD WXpusher.py /app
ADD main.py /app
ADD requirements.txt /app

RUN pip install -r requirements.txt

ENV webdriver=""
ENV username=""
ENV password=""
ENV tgbot_chat_id=""
ENV tgbot_token=""
ENV wxpusher_uid=""

CMD python -u /app/main.py --webdriver=$webdriver --username=$username --password=$password --tgbot_chat_id=$tgbot_chat_id --tgbot_token=$tgbot_token --wxpusher_uid=$wxpusher_uid
