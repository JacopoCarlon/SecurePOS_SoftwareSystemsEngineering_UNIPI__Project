import logging
import threading

import pandas as pd

from evaluation_system.label import Label
from evaluation_system.label_store import LabelStore


class LabelStoreController:
    def __init__(self):
        """
        Need to keep count of labels from expert and classifier,
        will increase count upon label storing, based on label_source field value.
        """
        self.num_labels_from_expert = 0
        self.num_labels_from_classifier = 0
        self.store = LabelStore()
        # report generator
        # control access to db ? (if local for each instance, not needed)

    def update_count_labels(self, label_source):
        if label_source == 'classifier':
            self.tot_labels_from_classifier += 1
        elif label_source == 'expert':
            self.tot_labels_from_expert += 1
        else:
            logging.error(f'Non standard label is being processed in EvalSys; \nlabel_src : {label_source}')
            raise ValueError("Evaluation System working on unknown-origin label")




