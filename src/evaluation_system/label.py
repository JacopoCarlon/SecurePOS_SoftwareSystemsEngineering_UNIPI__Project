
class Label:

    def __init__(self, session_id, label_value, label_source):
        self.uuid = session_id
        self.label_value = label_value
        self.label_source = label_source

    def to_dict(self):
        return {
            'uuid':
                self.uuid,
            'label_value':
                self.label_value,
            'label_source':
                self.label_source
        }
