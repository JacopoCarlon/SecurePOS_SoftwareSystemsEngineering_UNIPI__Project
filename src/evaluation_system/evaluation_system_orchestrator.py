"""Evaluation System Orchestrator : loads all configs and runs the listening server"""
import json
import logging
import threading
import os
import utility
from utility.json_validation import validate_json_data_file
from utility.ip_validation import ipv4_tester
from evaluation_system.label_store_controller import LabelStoreController
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi


class EvaluationSystemOrchestrator:
    """
    Orchestrator class for all Evaluation System functions
    """
    def __init__(self):
        """
        Initializes relative paths to configuration json(s), and respective schema(s)
        """
        self.config_path_rel = "evaluation_system/configs/eval_config.json"
        self.config_schema_path_rel = "evaluation_system/configs/eval_config_schema.json"
        self.label_store_controller = LabelStoreController()
        self.config = None
        self.ip_path_rel = "evaluation_system/configs/eval_ip_config.json"
        self.ip_path_schema_rel = "evaluation_system/configs/eval_ip_config_schema.json"
        self.ip_config = None

    def load_config(self):
        """
        Loads evaluation system configuration file, and validates it
        :return:
        """
        ev_conf_path = os.path.join(utility.data_folder, self.config_path_rel)
        with open(ev_conf_path, "r", encoding="UTF-8") as ev_file:
            ev_config = json.load(ev_file)
        if not validate_json_data_file(ev_config, self.config_schema_path_rel):
            logging.error("Impossible to load the evaluation system :\n"
                          "configuration: JSON file is not valid")
            raise ValueError("Evaluation System configuration failed")
        logging.info("Evaluation System configured correctly")
        self.config = ev_config

    def load_ip_config(self):
        """
        Loads ip and port to listen to
        :return:
        """
        ev_ip_path = os.path.join(utility.data_folder, self.ip_path_rel)
        with open(ev_ip_path, "r", encoding="UTF-8") as ip_file:
            ip_config = json.load(ip_file)
        if not validate_json_data_file(ip_config, self.ip_path_schema_rel):
            logging.error("Impossible to load the evaluation system :\n"
                          "configuration: JSON file is not valid")
            raise ValueError("Evaluation System configuration failed")
        logging.info("Ip and port of Evaluation System configured correctly")
        # test IP
        trg_ip = ip_config["ipv4_address"]
        if not ipv4_tester(trg_ip):
            print("Ipv4 address not valid")
            raise ValueError("Ipv4 address bad value")
        # test port
        trg_port = ip_config["port"]
        if trg_port not in range(0, 65535+1):
            print("Ipv4 port not valid")
            raise ValueError("Ipv4 port bad value")
        self.ip_config = ip_config

    def create_tables(self):
        """
        Creates DB tables for expertLabels and classifierLabels
        :return:
        """
        logging.info("Create tables (if not exists) for label storage")
        query = "CREATE TABLE if not exists expertLabelTable" \
                "(session_id TEXT PRIMARY KEY UNIQUE, value TEXT)"
        self.label_store_controller.store.ls_create_table(query, [])
        query = "CREATE TABLE if not exists classifierLabelTable" \
                "(session_id TEXT PRIMARY KEY UNIQUE, value TEXT)"
        self.label_store_controller.store.ls_create_table(query, [])

    def handle_message(self, incoming_label_json):
        """
        Message handler, generates a thread to serve the incoming label
        :param incoming_label_json:
        :return:
        """
        # When the system receives a message,
        # generate a new thread to manage label store and report generation!
        logging.info("Received label, creating new thread")
        thread = threading.Thread(target=self.label_store_controller.store_label,
                                  args=(self.config["min_labels_opinionated"], incoming_label_json))
        thread.start()

    def start_server(self):
        """Start the REST server, at the given IPv4 and Port, and assigns handler"""
        trg_ip_listen_on = self.ip_config["ipv4_address"]
        trg_port_listen_on = self.ip_config["port"]
        # Instantiate server
        logging.info("Start server for receiving labels")
        server = ServerREST()
        server.api.add_resource(ReceiveJsonApi,
                                "/",
                                resource_class_kwargs={
                                    'handler': self.handle_message
                                })
        server.run(debug=False, host=trg_ip_listen_on, port=trg_port_listen_on)

    def run(self):
        """Orchestrator loads config, prepares DB, and starts REST server"""
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
