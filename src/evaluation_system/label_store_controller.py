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
        self.enough_total_labels = False
        self.enough_matching_labels = False # redundancy value, can be only local
        self.store = LabelStore()
        # report generator
        # control access to db ? (if local for each instance, not needed)

    def update_count_labels(self, label_source):
        if label_source == 'classifier':
            self.num_labels_from_classifier += 1
        elif label_source == 'expert':
            self.num_labels_from_expert += 1
        else:
            logging.error(f'Non standard label is being processed in EvalSys; \nlabel_src : {label_source}')
            raise ValueError("Evaluation System working on unknown-origin label")

    def store_label(self, monitoring_window_length: int, label):
        logging.info("Label storage")
        # receive labels as json, need to convert them to Label object.
        session_id = label["session_id"]
        label_value = label["value"]
        label_source = label["source"]
        label = Label(session_id, label_value, label_source)
        label_dataframe = pd.DataFrame(label.to_dict(), index=[0],
                                       columns=["session_id", "value"])
        if label.label_source == "classifier":
            self.store.ls_store_label_df(label_dataframe, 'classifierLabel')
            self.update_count_labels('classifier')
        elif label.label_source == "expert":
            self.store.ls_store_label_df(label_dataframe, 'expertLabel')
            self.update_count_labels('expert')
        else:
            logging.error(f'Non standard label arrived to store_label in EvalSys;\nlabel_src : {label.label_source}')
            raise ValueError("Evaluation System working on unknown-origin label")

        # TODO !
        # should threshold apply to all, or only to matching ones ??
        # because this changes where the check shoudl be made

        if not self.enough_total_labels:
            if self.num_labels_from_expert >= monitoring_window_length and \
                    self.num_labels_from_classifier >= monitoring_window_length:
                self.enough_total_labels = True

        logging.info("Enough labels to generate a report")
        print("generate report")

        # load labels that have opinion from classifier AND expert, matching on uuid
        load_matching_labels_query = \
            "SELECT expertLT.session_id, " \
            "expertLT.value as expertValue," \
            "classifierLT.value as classifierValue " \
            "FROM expertLabelTable AS expertLT " \
            "INNER JOIN classifierLabelTable AS classifierLT " \
            "ON expertLT.session_id = classifierLT.session_id"
        opinionated_labels = self.store.ls_select_labels(load_matching_labels_query)

        opinionated_session_id_list = opinionated_labels["session_id"].to_list()

        num_usable_labels = len(opinionated_session_id_list)
        if num_usable_labels >= monitoring_window_length:
            self.enough_matching_labels = True

        if self.enough_matching_labels:
            print("DEBUG")
            # TODO !
            # if enough labels to pass threshold, free them from db

            # TODO !
            # generate report if all is good, else not ...
            self.enough_matching_labels = False



