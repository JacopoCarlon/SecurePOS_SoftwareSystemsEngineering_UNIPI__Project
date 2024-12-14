"""
    module for Evaluation Report object class
"""


class EvaluationReport:
    """
        Evaluation Report class object
    """

    def __init__(self):
        self.config = None

        self.num_compared_labels = 0
        self.num_conflicting_labels = 0
        self.measured_max_consecutive_conflicting_labels = 0
        self.threshold_conflicting_labels = 10
        self.threshold_max_consecutive_conflicting_labels = 5

    def to_dict(self):
        """
            Convert object to json
            :return: json formatted object
        """
        return {
            'num_compared_labels':
                self.num_compared_labels,
            'num_conflicting_labels':
                self.num_conflicting_labels,
            'measured_max_consecutive_conflicting_labels':
                self.measured_max_consecutive_conflicting_labels,
            'threshold_conflicting_labels':
                self.threshold_conflicting_labels,
            'threshold_max_consecutive_conflicting_labels':
                self.threshold_max_consecutive_conflicting_labels
        }
