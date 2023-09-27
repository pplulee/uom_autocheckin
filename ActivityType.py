class ActivityType:
    xpath = {"Lab": "/html/body/div[2]/div/div[1]",
             "Lecture": "/html/body/div[2]/div/div[2]",
             "Plenary": "/html/body/div[2]/div/div[3]",
             "Practical": "/html/body/div[2]/div/div[4]",
             "Seminar": "/html/body/div[2]/div/div[5]",
             "Tutorial": "/html/body/div[2]/div/div[6]",
             "Workshop": "/html/body/div[2]/div/div[7]",
             "Other": "/html/body/div[2]/div/div[8]"}


def find_activity_type(data):
    index = -1
    activity_types = [activity_type.upper() for activity_type in ActivityType.xpath.keys()]
    for activity_type in activity_types:
        if activity_type in data:
            index = activity_types.index(activity_type)
            break
    return index
