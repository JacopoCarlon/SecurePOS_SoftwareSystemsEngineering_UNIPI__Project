from utility.json_validation import validate_json
import utility
import json
import logging


class EvaluationReport:

    def __init__(self):
        self.config_path = f'{utility.data_folder}/evaluation_system/configs/eval_config.json'
        self.config_schema_path = f'{utility.data_folder}/evaluation_system/configs/eval_config_schema.json'
        self.config = None

        self.num_compared_labels = 0
        self.num_conflicting_labels = 0
        self.measured_max_consecutive_conflicting_labels = 0
        self.threshold_conflicting_labels = 10
        self.threshold_max_consecutive_conflicting_labels = 5
        self.load_config()

    def to_dict(self):
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

    def load_config(self):
        with open(self.config_path, "r", encoding="UTF-8") as file:
            config = json.load(file)
        with open(self.config_schema_path, "r", encoding="UTF-8") as file:
            config_schema = json.load(file)
        if not validate_json(config, config_schema):
            logging.error("Impossible to load the evaluation system, \nconfiguration: JSON file is not valid")
            raise ValueError("Evaluation System configuration failed")
        logging.info("Evaluation System configuring EvaluationReport")
        self.config = config
        self.threshold_conflicting_labels = \
            self.config["max_conflicting_labels_threshold"]
        self.threshold_max_consecutive_conflicting_labels = \
            self.config["max_consecutive_conflicting_labels_threshold"]
