
class Label:

    def __init__(self, session_id, value, source):
        self.session_id = session_id
        self.source = source
        self.value = value

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'source': self.source,
            'value': self.value
        }
