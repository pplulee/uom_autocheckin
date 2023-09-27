import datetime

import icalendar
import pytz
from requests import get

from ActivityType import ActivityType, find_activity_type

london_timezone = pytz.timezone('Europe/London')


def phrase(text):
    text = text.replace("_", " ")
    text = text.replace("&", " ")
    return text


class Timetable:
    def __init__(self, ics_url):
        self.ics_url = ics_url
        self.today = []

    def refresh_today(self):
        today = []
        response = get(self.ics_url)
        if response.status_code == 200:
            ics_file = response.text
        else:
            return False
        ics = icalendar.Calendar.from_ical(ics_file)
        # 提取当天的课程
        for event in ics.walk('vevent'):
            if event['dtstart'].dt.date() == datetime.date.today():
                this_class = {}
                info = str(event['summary']).split('/')
                if len(info) < 3:
                    continue
                this_class['unit'] = info[0]
                type = info[1]
                if (type_index := find_activity_type(type)) == -1:
                    this_class['type'] = phrase(type)
                else:
                    this_class['type'] = list(ActivityType.xpath.keys())[type_index]
                this_class['location'] = phrase(str(event.get('location')))
                this_class['time'] = event['dtstart'].dt.astimezone(london_timezone).strftime("%Y-%m-%d %H:%M:%S")
                # 时间已过
                if datetime.datetime.strptime(this_class['time'], "%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
                    continue
                today.append(this_class)
        today = sorted(today, key=lambda x: x['time'])
        self.today = today
        return True

    def get_next_class(self, pop=False):
        if not self.today:
            return None
        next_class = self.today[0]
        if pop:
            self.today.pop(0)
        return next_class
