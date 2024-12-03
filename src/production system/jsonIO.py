import json


class jsonIO:
    def __init__(self):
        with open('src/production system/.env') as f:
            data = json.load(f)
            self.address = data['jsonIOaddress']
            self.port = data['jsonIOport']

    def receive_message(self):
        pass

    def send_message(self, message):
        pass