import json
import logging
import requests
from typing import Callable

from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi
from utility.json_validation import validate_json_data_file


class DevSysCommunicationController:

    def __init__(self, conf_file_path: str, conf_schema_path):
        with open(conf_file_path, "r", encoding="UTF-8") as file:
            conf_json = json.load(file)

        if not validate_json_data_file(conf_json, conf_schema_path):
            logging.error("Impossible to load the development system "
                          "configuration: JSON file is not valid")
            raise ValueError("Development System configuration failed")

        self.ip_address = conf_json['ip_address']
        self.port = conf_json['port']
        self.production_system_url = conf_json['production_system_url']

    def start_rest_server(self, json_schema_path: dict, handler: Callable[[dict], None]) -> None:
        """
        Starts rest server for json file reception
        :param json_schema_path: schema for json validation
        :param handler: handler function
        :return:
        """
        server = ServerREST()
        server.api.add_resource(
            ReceiveJsonApi,
            "/",
            resource_class_kwargs={
                'json_schema_path': json_schema_path,
                'handler': handler
            })
        server.run(host=self.ip_address, port=self.port, debug=False)

    def send_model_to_production(self, model_file_path):
        try:
            with open(model_file_path, "rb") as model_file:
                response = requests.post(self.production_system_url, files={'file': model_file})
            if not response.ok:
                logging.error("Failed to send the classifier to Production System")
            else:
                print("Classifier sent to the Production System")

        except requests.exceptions.RequestException as ex:
            logging.error(f'Error during the send of the classifier: {ex}')

