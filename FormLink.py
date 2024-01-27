import datetime


class FormLink:
    def __init__(self):
        self.links = [
            {"begin": datetime.date(2024, 1, 8), "end": datetime.date(2024, 1, 26),
             "link": "https://uom.link/january-check-in"},
            {"begin": datetime.date(2024, 1, 29), "end": datetime.date(2024, 2, 4),
             "link": "https://forms.office.com/e/XmE0UUxvM7"},
            {"begin": datetime.date(2024, 2, 5), "end": datetime.date(2024, 2, 11),
             "link": "https://forms.office.com/e/BXWr8ruANY"},
            {"begin": datetime.date(2024, 2, 12), "end": datetime.date(2024, 2, 18),
             "link": "https://forms.office.com/e/aNxt2nMHLJ"},
            {"begin": datetime.date(2024, 2, 19), "end": datetime.date(2024, 2, 25),
             "link": "https://forms.office.com/e/LJ3T5Pcimu"},
            {"begin": datetime.date(2024, 2, 26), "end": datetime.date(2024, 3, 3),
             "link": "https://forms.office.com/e/99GDT3n7vz"},
        ]

    def get_link(self):
        today = datetime.datetime.now().date()
        for link in self.links:
            if link["begin"] <= today <= link["end"]:
                return link["link"]
        return None
