
class Label:

    def __init__(self, session_id, label_value, label_source):
        self.uuid = session_id
        self.label_value = label_value
        self.label_source = label_source

    def to_dict(self):
        return {
            'session_id':
                self.uuid,
            'value':
                self.label_value,
            'source':
                self.label_source
        }

    def to_dict_no_src(self):
        return {
            'session_id':
                self.uuid,
            'value':
                self.label_value,
            }