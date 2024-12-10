import json
import logging
import threading  # for db access ?
from evaluation_system.label_store_controller import LabelStoreController


class EvaluationSystemOrchestrator:

    def __init__(self):
        self.label_store_controller = LabelStoreController()
        self.config_path = "../../data/evaluation_system/configs/eval_config.json"
        self.config_schema_path = "../../data/evaluation_system/configs/eval_config_schema.json"
        self.config = None

    def load_config(self):
        with open(self.config_path, "r", encoding="UTF-8") as file:
            ev_config = json.load(file)
        with open(self.config_schema_path, "r", encoding="UTF-8") as file:
            config_schema = json.load(file)
        if not validate_json(ev_config, config_schema):
            logging.error("Impossible to load the monitoring system "
                          "configuration: JSON file is not valid")
            raise ValueError("Monitoring System configuration failed")
        logging.info("Monitoring System configured correctly")
        self.config = config