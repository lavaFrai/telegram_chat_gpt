import json


class Config:
    def __init__(self):
        data = json.load(open("conf/config.json"))
        self.telegram_token = data["telegram_token"]
        self.openai_token = data["openai_token"]
