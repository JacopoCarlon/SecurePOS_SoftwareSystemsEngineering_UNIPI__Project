import json
import logging
import threading


class EvaluationSystemController:

    def __init__(self):
        self.config_path = "../../data/evaluation_system/conf/config.json"
        self.config_schema_path = "../../data/evaluation_system/conf/config_schema.json"
        self.config = None
