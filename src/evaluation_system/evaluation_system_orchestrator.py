import json
import logging
import threading # for db access ?
from evaluation_system.label_store_controller import LabelStoreController


class EvaluationSystemOrchestrator:

    def __init__(self):
        self.label_store_controller = LabelStoreController()
        self.config_path = "../../data/evaluation_system/conf/config.json"
        self.config_schema_path = "../../data/evaluation_system/conf/config_schema.json"
        self.config = None
