import datetime


class FormLink:
    def __init__(self):
        self.links = [
            {"begin": datetime.date(2024, 3, 4), "end": datetime.date(2024, 3, 10),
             "link": "https://forms.office.com/e/Eh9p7GwrF5"},
            {"begin": datetime.date(2024, 3, 11), "end": datetime.date(2024, 3, 17),
             "link": "https://forms.office.com/e/eEscAgS4S6"},
            {"begin": datetime.date(2024, 3, 18), "end": datetime.date(2024, 3, 24),
             "link": "https://forms.office.com/e/ZhZMcsmtPN"},
            {"begin": datetime.date(2024, 4, 8), "end": datetime.date(2024, 4, 14),
             "link": "https://forms.office.com/e/CX8EybxAAT "},
        ]

    def get_link(self):
        today = datetime.datetime.now().date()
        for link in self.links:
            if link["begin"] <= today <= link["end"]:
                return link["link"]
        return None
