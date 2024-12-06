import json
from comms import ServerREST
from comms.file_transfer_api import FileReceptionAPI

RECEIVED_FILE_NAME = "development_system_data/learning_sets.json"


class DevSysCommunicationController:

    def __init__(self, conf_file_path: str):
        with open(conf_file_path, "r", encoding="UF-8") as file:
            conf_json = json.load(file)

            self.ip_address = conf_json['ip_address']
            self.port = conf_json['port']
            self.production_system_url = conf_json['production_system_url']

    def start_rest_server(self) -> None:
        """
        Starts rest server for file reception
        :return:
        """
        server = ServerREST()
        server.api.add_resource(
            FileReceptionAPI,
            "/fileTransfer",
            kwargs={
                'filename': RECEIVED_FILE_NAME
            })
        server.run(host=self.ip_address, port=self.port, debug=False)
