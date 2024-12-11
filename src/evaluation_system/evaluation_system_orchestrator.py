import json
import logging
import threading
from utility.json_validation import validate_json
from evaluation_system.label_store_controller import LabelStoreController
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi


TESTING = False


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
            logging.error("Impossible to load the evaluation system :\n configuration: JSON file is not valid")
            raise ValueError("Evaluation System configuration failed")
        logging.info("Evaluation System configured correctly")
        self.config = config_schema

    def create_tables(self):
        logging.info("Create tables (if not exists) for label storage")
        query = "CREATE TABLE if not exists expertLT" \
                "(session_id TEXT PRIMARY KEY UNIQUE, value TEXT)"
        self.label_store_controller.store.ls_create_table(query)
        query = "CREATE TABLE if not exists classifierLT" \
                "(session_id TEXT PRIMARY KEY UNIQUE, value TEXT)"
        self.label_store_controller.store.ls_create_table(query)

    def handle_message(self, incoming_label_json):
        if not TESTING:
            # When the system receives a message,
            # generate a new thread to manage label store and report generation!
            logging.info("Received label, creating new thread")
            thread = threading.Thread(target=self.label_store_controller.store_label,
                                      args=(self.config["min_labels_opinionated"], incoming_label_json))
            thread.start()

    def start_server(self):
        # Instantiate server
        logging.info("Start server for receiving labels")
        server = ServerREST()
        server.api.add_resource(ReceiveJsonApi,
                                "/",
                                resource_class_kwargs={
                                    'handler': self.handle_message
                                })
        server.run(debug=False, port=8001)

    def run(self):
        # validate and load evaluation system configuration
        self.load_config()
        # create LOCAL sqlite3 db tables, for 2 types of labels from ProductionSystem
        self.create_tables()
        # wait for labels at a given IP .
        # as soon as a label arrives, start a thread to :
        # -> store it properly, and(if...) generate the report
        self.start_server()
