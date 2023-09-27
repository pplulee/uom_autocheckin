FROM python:3.9-slim

# 设置时区
ENV TZ=Europe/London
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
ADD ActivityType.py /app
ADD School.py /app
ADD FormLink.py /app
ADD Timetable.py /app
ADD main.py /app
ADD requirements.txt /app

RUN pip install -r requirements.txt

ENV studentID=""
ENV school=""
ENV email=""
ENV username=""
ENV password=""
ENV webdriver=""
ENV tgbot_chat_id=""
ENV tgbot_token=""
ENV ics_url=""


CMD python -u /app/main.py --studentID "$studentID" --school "$school" --email "$email" --username "$username" --password "$password" --webdriver "$webdriver" --tgbot_chat_id "$tgbot_chat_id" --tgbot_token "$tgbot_token" --ics_url "$ics_url"
