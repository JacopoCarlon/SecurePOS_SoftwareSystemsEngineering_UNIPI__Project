"""
This module is used to manage the communication between the
segregation system and the other systems.
"""
import json
import os
from typing import Callable
import requests
from utility import data_folder
from flask_restful import Resource
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi

FILE_PATH = os.path.join(data_folder, 'segregation_system', 'input')
CONFIG_PATH = os.path.join(data_folder, 'segregation_system', 'config', 'segregation_config.json')

class HealthCheckApi(Resource):
    """
    Health check endpoint to verify the server is running.
    """
    def get(self):
        return "Server is running", 200

class CommunicationController:
    def __init__(self):
        with open(CONFIG_PATH, 'r', encoding="UTF-8") as file:
            config = json.load(file)
            self.ip_address = config["segregationSystemIpAddress"]
            self.port = config["segregationSystemPort"]
            self.development_system_url = config["developmentSystemEndpoint"]
            self.server = None
            self.check = config["checkServerEndpoint"]

    def is_server_running(self) -> bool:
        """
        Check if the REST server is already running by sending a request to the health endpoint.
        :return: True if the server is running, False otherwise.
        """
        try:
            response = requests.get(self.check, timeout=5)
            if response.status_code == 200:
                print("REST server is already running.")
                return True
        except requests.ConnectionError:
            print("REST server is not running.")
        return False

    def start_server(self, json_schema_path: dict, handler: Callable[[dict], None]) -> None:
        self.server = ServerREST()

        self.server.api.add_resource(
            HealthCheckApi,
            "/health",
            resource_class_kwargs={}
        )

        self.server.api.add_resource(
            ReceiveJsonApi,
            "/",
            resource_class_kwargs={
                'json_schema_path': json_schema_path,
                'handler': handler
            })
        self.server.run(host=self.ip_address, port=self.port, debug=False)

    def send_json(self, url, json_data):
        """
        Function used to send a json to a generic URL.
        Used for testing
        :return:
        """
        try:
            requests.post(url,
                          json=json_data,
                          timeout=20)
        except requests.exceptions.RequestException as e:
            print("Error during the send of message: ", e)

    def send_learning_sets(self, learning_sets):
        try:
            with open(learning_sets, 'r', encoding="UTF-8") as file:
                data = json.load(file)
                print(data)

            response = requests.post(
                self.development_system_url, json=data,
                timeout=20
            )
            if not response.ok:
                print("Failed to send the learning sets")
            else:
                print("Learning sets sent")

        except requests.exceptions.RequestException as ex:
            print(f'Error during the send of the learning sets: {ex}')
