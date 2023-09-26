import datetime


class FormLink:
    def __init__(self):
        self.links = [
            {"begin": datetime.date(2023, 9, 25), "end": datetime.date(2023, 10, 1),
             "link": "https://forms.office.com/e/aDPtrMNc0s"},
            {"begin": datetime.date(2023, 10, 2), "end": datetime.date(2023, 10, 8),
             "link": "https://forms.office.com/e/6ff1ZF5snP"},
            {"begin": datetime.date(2023, 10, 9), "end": datetime.date(2023, 10, 15),
             "link": "https://forms.office.com/e/GdKa9hM6qv"},
            {"begin": datetime.date(2023, 10, 16), "end": datetime.date(2023, 10, 22),
             "link": "https://forms.office.com/e/Bpypz8ZBf1"},
            {"begin": datetime.date(2023, 10, 23), "end": datetime.date(2023, 10, 29),
             "link": "https://forms.office.com/e/ZgESEFSyar"},
            {"begin": datetime.date(2023, 10, 30), "end": datetime.date(2023, 11, 5),
             "link": "https://forms.office.com/e/z7vh0nL1pS"},
            {"begin": datetime.date(2023, 11, 6), "end": datetime.date(2023, 11, 12),
             "link": "https://forms.office.com/e/1Ae5RrR11i"},
            {"begin": datetime.date(2023, 11, 13), "end": datetime.date(2023, 11, 19),
             "link": "https://forms.office.com/e/VvitPUa1UJ"},
            {"begin": datetime.date(2023, 11, 20), "end": datetime.date(2023, 11, 26),
             "link": "https://forms.office.com/e/d3xpVq0HyY"},
            {"begin": datetime.date(2023, 11, 27), "end": datetime.date(2023, 12, 3),
             "link": "https://forms.office.com/e/qMA5rfuxep"},
            {"begin": datetime.date(2023, 12, 4), "end": datetime.date(2023, 12, 10),
             "link": "https://forms.office.com/e/xRuxxZWUMS"},
            {"begin": datetime.date(2023, 12, 11), "end": datetime.date(2023, 12, 17),
             "link": "https://forms.office.com/e/nAMQ2TPnrf"},
        ]

    def get_link(self):
        today = datetime.date.today()
        for link in self.links:
            if link["begin"] <= today <= link["end"]:
                return link["link"]
        return None
