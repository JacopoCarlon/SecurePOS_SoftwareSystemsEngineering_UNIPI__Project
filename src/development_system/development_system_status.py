"""
This module contains a class for handling the internal status of the Development System
"""
import os
import json


class DevelopmentSystemStatus:
    def __init__(self, status_file):
        self.status_file = status_file
        if os.path.isfile(status_file):
            with open(status_file, "r", encoding="UTF-8") as file:
                self.status = json.load(file)
        else:
            self.status = {
                "phase": "Waiting"
            }

    def update_status(self, new_status: dict):
        self.status.update(new_status)
        with open(self.status_file, "w", encoding="UTF-8") as file:
            json.dump(self.status, file)

    def get_phase(self):
        return self.status['phase']

    def first_iter(self):
        return "max_iter" not in self.status

    def get_training_params(self):
        params = {
            "max_iter": self.status['max_iter']
        }
        params.update(self.status['avg_params'])
        return params

    def get_best_classifier_data(self):
        return self.status["best_classifier_data"]

    def retry(self):
        self.status = {"phase": "Ready"}
        with open(self.status_file, "w", encoding="UTF-8") as file:
            json.dump(self.status, file)

    def reset(self):
        self.status = {"phase": "Waiting"}
        with open(self.status_file, "w", encoding="UTF-8") as file:
            json.dump(self.status, file)
