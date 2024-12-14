"""module containing Label class"""


class Label:
    """
        Class for Label object type, with uuid, value and source
    """
    def __init__(self, session_id, label_value, label_source):
        self.uuid = session_id
        self.label_value = label_value
        self.label_source = label_source

    def to_dict(self):
        """
        Convert Label class into dictionary object
        :return:
        """
        return {
            'session_id':
                self.uuid,
            'value':
                self.label_value,
            'source':
                self.label_source
        }
