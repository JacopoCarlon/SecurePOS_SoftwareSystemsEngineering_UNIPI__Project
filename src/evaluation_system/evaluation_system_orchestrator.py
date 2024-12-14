import json
import logging
import threading
import os
import re
import utility
from utility.json_validation import validate_json_data_file
from evaluation_system.label_store_controller import LabelStoreController
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi
from utility.ip_validation import ipv4_tester

class EvaluationSystemOrchestrator:

    def __init__(self):
        self.label_store_controller = LabelStoreController()
        self.config_path_rel = f'evaluation_system/configs/eval_config.json'
        self.config_schema_path_rel = f'evaluation_system/configs/eval_config_schema.json'
        self.config = None
        self.ip_path_rel = f'evaluation_system/configs/eval_ip_config.json'
        self.ip_path_schema_rel = f'evaluation_system/configs/eval_ip_config_schema.json'
        self.ip_listen_on = None
        self.port_listen_on = None

    def load_config(self):
        ev_conf_path = os.path.join(utility.data_folder, self.config_path_rel)
        with open(ev_conf_path, "r", encoding="UTF-8") as ev_file:
            ev_config = json.load(ev_file)
        if not validate_json_data_file(ev_config, self.config_schema_path_rel):
            logging.error("Impossible to load the evaluation system :\n configuration: JSON file is not valid")
            raise ValueError("Evaluation System configuration failed")
        logging.info("Evaluation System configured correctly")
        self.config = ev_config

    def load_ip_config(self):
        ev_ip_path = os.path.join(utility.data_folder, self.ip_path_rel)
        with open(ev_ip_path, "r", encoding="UTF-8") as ip_file:
            ip_config = json.load(ip_file)
        if not validate_json_data_file(ip_config, self.ip_path_schema_rel):
            logging.error("Impossible to load the evaluation system :\n configuration: JSON file is not valid")
            raise ValueError("Evaluation System configuration failed")
        logging.info("Ip and port of Evaluation System configured correctly")
        # test IP
        trg_ip = ip_config["ipv4_address"]
        if not ipv4_tester(trg_ip):
            print("Ipv4 not valid")
        # test port
        trg_port = ip_config["port"]

        self.ip_listen_on = trg_ip
        self.port_listen_on = trg_port

    def create_tables(self):
        logging.info("Create tables (if not exists) for label storage")
        query = "CREATE TABLE if not exists expertLabelTable" \
                "(session_id TEXT PRIMARY KEY UNIQUE, value TEXT)"
        self.label_store_controller.store.ls_create_table(query, [])
        query = "CREATE TABLE if not exists classifierLabelTable" \
                "(session_id TEXT PRIMARY KEY UNIQUE, value TEXT)"
        self.label_store_controller.store.ls_create_table(query, [])

    def handle_message(self, incoming_label_json):
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
        server.run(debug=False, host=self.ip_listen_on, port=self.port_listen_on)

    def run(self):
        # validate and load evaluation system configuration
        self.load_config()
        print("Sampling range and Threshold values loaded from eval_config file")
        # load ip and port configuration
        self.load_ip_config()
        print("Target IPv4 and port loaded from ip_config file")
        # create LOCAL sqlite3 db tables, for 2 types of labels from ProductionSystem
        self.create_tables()
        print("DataBase created")
        # wait for labels at a given IP .
        # as soon as a label arrives, start a thread to :
        # -> store it properly, and(if...) generate the report
        print("starting REST server")
        self.start_server()
