import json

import jsonIO

class PrepareSessionHandler:

    # Constructor
    def __init__(self):
        self.new_session()

    def session_request(self):
        #create json with class variables
        data = {
            'uuid': self.uuid,
            'label': self.label,
            'median_coordinates': [self.median_coordinates[0], self.median_coordinates[1]],
            'mean_diff_time': self.mean_diff_time,
            'mean_diff_amount': self.mean_diff_amount,
            'mean_target_ip': self.mean_target_ip,
            'mean_dest_ip': self.mean_dest_ip
        }

        #send the json
        return data

    def new_session(self):
        #retrieve the message from the jsonIO
        message = jsonIO.jsonIO().receive_message()

        #parse the message
        self.uuid = message['uuid']
        self.label = message['label']
        self.median_coordinates = message['median_coordinates']
        self.mean_diff_time = message['mean_diff_time']
        self.mean_diff_amount = message['mean_diff_amount']
        self.mean_target_ip = message['mean_target_ip']
        self.mean_dest_ip = message['mean_dest_ip']
        
        


    