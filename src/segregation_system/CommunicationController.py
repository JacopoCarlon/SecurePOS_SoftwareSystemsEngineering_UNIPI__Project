import json
from typing import Callable
import requests
from flask_restful import Resource
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi
import os
from utility import data_folder

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
        with open(CONFIG_PATH, 'r') as file:
            config = json.load(file)
            self.ip_address = config["segregationSystemIpAddress"]
            self.port = config["segregationSystemPort"]
            self.development_system_url = config["developmentSystemEndpoint"]
            self.server = None

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

    def send_learning_sets(self, learning_sets):
        try:
            with open(learning_sets, 'r') as file:
                data = json.load(file)
                print(data)

            response = requests.post(self.development_system_url, json=data)
            if not response.ok:
                print("Failed to send the learning sets")
            else:
                print("Learning sets sent")

        except requests.exceptions.RequestException as ex:
            print(f'Error during the send of the learning sets: {ex}')
