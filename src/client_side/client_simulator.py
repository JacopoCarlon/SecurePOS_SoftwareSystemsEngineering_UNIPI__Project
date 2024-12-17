import os
import csv
import time
import json
import threading
import requests
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi
from utility import data_folder

SCENARIO_JSON = os.path.join(data_folder, "client_side/scenario.json")
RAW_DATA_FILES = [
    os.path.join(data_folder, "client_side/raw_data/localizationSys.csv"),
    os.path.join(data_folder, "client_side/raw_data/networkMonitor.csv"),
    os.path.join(data_folder, "client_side/raw_data/labels.csv"),
    os.path.join(data_folder, "client_side/raw_data/transactionCloud.csv")
]


class ClientSimulator:
    def __init__(self):
        with open(SCENARIO_JSON, "r", encoding="UTF-8") as scenario_file:
            scenario = json.load(scenario_file)

        self.scenario_type = scenario["scenario"]
        self.ingestion_system_url = scenario['ingestion_system_url']
        self.sleep_time = scenario["sleep_time"]
        self.repetitions = scenario["repetitions"]
        self.testing = scenario["testing"]

        self.end_of_test = False
        self.cv = threading.Condition()

        if self.testing:
            self.data = {
                "ingestion_system": 0,
                "segregation_system": 0,
                "development_system": 0,
                "production_system": 0,
                "evaluation_system": 0
            }

            flask_thread = threading.Thread(
                target=self.server_thread,
                args=(scenario['ip_address'], scenario['port'])
            )
            flask_thread.daemon = True
            flask_thread.start()

    def server_thread(self, ip_address, port):
        server = ServerREST()
        server.api.add_resource(
            ReceiveJsonApi,
            "/",
            resource_class_kwargs={
                'handler': self.receive_message
            }
        )
        server.run(ip_address, port)

    def receive_message(self, received_json: dict):
        self.data[received_json["system"]] += received_json["time"]
        if received_json["end"]:
            with self.cv:
                self.end_of_test = True
                self.cv.notify()

    def send_raw_data(self):
        datasets = []
        for csv_file_path in RAW_DATA_FILES:
            with open(csv_file_path, "r", encoding="UTF-8") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                datasets.append([row for row in csv_reader])

        max_rows = max(len(dataset) for dataset in datasets)

        for i in range(max_rows):
            for dataset in datasets:
                if i < len(dataset):
                    try:
                        requests.post(self.ingestion_system_url, json=dataset[i])
                    except requests.exceptions.RequestException as ex:
                        print(ex)
                    time.sleep(self.sleep_time)

    def dump_data(self, csv_results_path):
        header = [
            "ingestion_system",
            "segregation_system",
            "development_system",
            "production_system",
            "evaluation_system"
        ]
        with open(csv_results_path, "a+", encoding="UTF-8") as csv_file:
            writer = csv.DictWriter(csv_file, header)
            writer.writerow(self.data)

    def reset(self):
        self.end_of_test = False
        self.data = {
            "ingestion_system": 0,
            "segregation_system": 0,
            "development_system": 0,
            "production_system": 0,
            "evaluation_system": 0
        }

    def run(self):
        time_str = time.strftime("%d_%H_%M", time.localtime())
        file_name = "client_side/test_results/" \
                    f'{self.scenario_type}_' \
                    f'{self.repetitions}_reps_' \
                    f'{time_str}_results.csv'

        csv_results_path = os.path.join(data_folder, file_name)

        for i in range(self.repetitions):
            self.send_raw_data()

            # Wait before next iteration
            with self.cv:
                while not self.end_of_test:
                    self.cv.wait()

                if self.testing:
                    self.dump_data(csv_results_path)
                    self.reset()
