import json
from typing import Callable
import requests
from src.comms import ServerREST
from src.comms.json_transfer_api import ReceiveJsonApi

class CommunicationController:
    def __init__(self):
        self.ip_address = "192.168.97.250"
        self.port = 5003
        self.development_system_url = "http://192.168.97.185:5001/"
        self.server = None

    def start_server(self, json_schema_path: dict, handler: Callable[[dict], None]) -> None:
        self.server = ServerREST()
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
