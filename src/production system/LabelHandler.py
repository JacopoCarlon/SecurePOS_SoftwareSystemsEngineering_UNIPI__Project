import jsonIO

class LabelHandler:
    def __init__(self, label):
        self.uuid = label['uuid']
        self.label = label['label']

    def send_lable(phase='evaluation'):
        if phase == 'evaluation':
            #send the label to the evaluation
            jsonIO.jsonIO().send_message({'uuid': self.uuid, 'label': self.label})
            pass
        else:
            #send the label to the production system
            jsonIO.jsonIO().send_message({'uuid': self.uuid, 'label': self.label})
        pass