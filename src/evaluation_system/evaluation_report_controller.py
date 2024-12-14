"""Module providing the Evaluation Report Controller class"""
import json
import logging
from itertools import groupby
from datetime import datetime
from utility import data_folder

from evaluation_system.testing_state import TESTING
from evaluation_system.evaluation_report import EvaluationReport


class EvaluationReportController:
    """Class for generating the Evaluation Report"""

    def __init__(self):
        self.report = EvaluationReport()
        self.labels = None
        self.count_report = 0

    def generate_report_json(self):
        now = datetime.now()
        report_dict = self.report.to_dict()
        eval_record_dir = f'{data_folder}/evaluation_system/report'
        file_record_name = f'report-{now.strftime("%Y_%m_%d-%H_%M_%S")}'
        complete_record_path_name = f'{eval_record_dir}/{file_record_name}_{self.count_report}.json'

        # with open(complete_record_path_name, 'w', encoding="UTF-8") as json_file:
        #     json.dump(report_dict, json_file, indent="\t")
        json_file = open(complete_record_path_name, 'w', encoding="UTF-8")
        try:
            json.dump(report_dict, json_file, indent="\t")
        finally:
            json_file.flush()
            json_file.close()

        logging.info(f'Generated EvaluationReport json, file name : {file_record_name}')
        print(f'report has been saved in : {complete_record_path_name}')
        if TESTING:
            print(f'DBG, report reads : {report_dict}')

    def populate_conflicts_array(self, conf_array: list):
        for row in self.labels.index:
            expert_label = self.labels["expertValue"][row]
            classifier_label = self.labels["classifierValue"][row]
            conf_array.append(True if expert_label != classifier_label else False)

    def generate_report(self, label_dataframe):
        if TESTING:
            print(f'DBG, received labels df : {label_dataframe}')

        self.count_report += 1
        self.labels = label_dataframe

        if self.labels is not None:
            # we can do the evaluation properly !
            conflicts_array = []
            self.populate_conflicts_array(conflicts_array)

            self.report.num_compared_labels = len(conflicts_array)
            self.report.num_conflicting_labels = sum(conflicts_array)

            # find longest subsequence of conflicts
            safe_list = ["noConflictingLabels"]
            group_labels_df = groupby(conflicts_array, bool)
            longest_conflict = max([list(seq) for val, seq in group_labels_df if val is True],
                                   key=len,
                                   default=safe_list)

            if TESTING:
                print(f'longest conflict streak : {longest_conflict}')

            if longest_conflict == safe_list:
                longest_conflict = []

            self.report.measured_max_consecutive_conflicting_labels = len(longest_conflict)

            # generate report as json
            self.generate_report_json()
        return
