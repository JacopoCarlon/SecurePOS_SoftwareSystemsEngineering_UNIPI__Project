class EvaluationReport:

    def __init__(self):
        self.num_conflicting_labels = 0
        self.num_compared_labels = 0
        self.measured_max_consecutive_conflicting_labels = 0
        self.threshold_conflicting_labels = 10
        self.threshold_max_consecutive_conflicting_labels = 5

    def to_dict(self):
        return {
            'num_conflicting_labels':
                self.num_conflicting_labels,
            'num_compared_labels':
                self.num_compared_labels,
            'measured_max_consecutive_conflicting_labels':
                self.measured_max_consecutive_conflicting_labels,
            'threshold_conflicting_labels':
                self.threshold_conflicting_labels,
            'threshold_max_consecutive_conflicting_labels':
                self.threshold_max_consecutive_conflicting_labels
        }
