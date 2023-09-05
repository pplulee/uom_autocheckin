from requests import post


class WXpusher:
    def __init__(self, wxpusher_uid):
        self.API_TOKEN = "AT_MrNwhC7N9jbt2hmdDXxOaGPkI7OmN8WV"
        self.wxpusher_uid = wxpusher_uid
        self.baseurl = "https://wxpusher.zjiecode.com/api/send/message"

    def send_message(self, content):
        post(self.baseurl, data={'appToken': self.API_TOKEN,
                                 'content': content,
                                 'summary': 'UoM_AutoCheckin',
                                 'contentType': 1,
                                 'uids': [self.wxpusher_uid]}
             )
