"""
This module implements the orchestrator for the Development System
"""
import os
import json
import ipaddress
import threading
import pandas as pd
import joblib

from utility import data_folder
from development_system.dev_sys_communication_controller import DevSysCommunicationController
from development_system.training_orchestrator import TrainingOrchestrator
from development_system.validation_orchestrator import ValidationOrchestrator
from development_system.testing_orchestrator import TestingOrchestrator
import development_system.classifier_data as cld

# Json Schemas
COMM_CONFIG_SCHEMA_PATH = os.path.join(data_folder, "development_system/json_schemas/comm_config_schema.json")
LEARNING_SET_SCHEMA_PATH = os.path.join(data_folder, "development_system/json_schemas/learning_set_schema.json")
VAL_CONFIG_SCHEMA_PATH = os.path.join(data_folder, "development_system/json_schemas/val_config_schema.json")
TEST_CONFIG_SCHEMA_PATH = os.path.join(data_folder, "development_system/json_schemas/test_config_schema.json")

# Configuration files
COMMUNICATION_CONFIG_PATH = os.path.join(data_folder, "development_system/configs/communications_configuration.json")
VALIDATION_CONFIG_PATH = os.path.join(data_folder, "development_system/configs/validation_configuration.json")
TESTING_CONFIG_PATH = os.path.join(data_folder, "development_system/configs/testing_configuration.json")
STATUS_FILE_PATH = os.path.join(data_folder, "development_system/configs/status.json")

# Learning sets file
LEARNING_SETS_PATH = os.path.join(data_folder, "development_system/learning_sets.json")

# Classifier models folder
CLASSIFIER_FOLDER = os.path.join(data_folder, "development_system/classifiers/")

# Report files
LEARNING_CURVE_PATH = os.path.join(data_folder, "development_system/reports/learning_curve.png")
VALIDATION_REPORT_PATH = os.path.join(data_folder, "development_system/reports/validation_report.json")
TESTING_REPORT_PATH = os.path.join(data_folder, "development_system/reports/testing_report.json")

# Other
AUTO_TEST = False


class DevelopmentSystemOrchestrator:
    """
    Orchestrator class for development system
    """
    def __init__(self):
        self.cv = threading.Condition()
        self.communication_controller = DevSysCommunicationController(
            COMMUNICATION_CONFIG_PATH,
            COMM_CONFIG_SCHEMA_PATH
        )
        self.training_orchestrator = TrainingOrchestrator(
            LEARNING_CURVE_PATH
        )
        self.validation_orchestrator = ValidationOrchestrator(
            VALIDATION_CONFIG_PATH,
            VAL_CONFIG_SCHEMA_PATH,
            CLASSIFIER_FOLDER,
            VALIDATION_REPORT_PATH,
            self.training_orchestrator
        )
        self.testing_orchestrator = TestingOrchestrator(
            TESTING_CONFIG_PATH,
            TEST_CONFIG_SCHEMA_PATH,
            TESTING_REPORT_PATH
        )
        self.learning_sets = None
        self.received_data = None

    @staticmethod
    def ip_to_float(ip_string):
        return float(int(ipaddress.ip_address(ip_string)))\
               / float(int(ipaddress.ip_address("255.255.255.255")))

    def clean_learning_sets(self, data_json):
        sets = {}

        for set_name in data_json:
            dataframe = pd.DataFrame.from_dict(data_json[set_name])
            dataframe["median_targetIP"] = dataframe["median_targetIP"].apply(self.ip_to_float)
            dataframe["median_destIP"] = dataframe["median_destIP"].apply(self.ip_to_float)

            sets[set_name] = (
                dataframe.drop(["uuid", "label"], axis=1),
                dataframe["label"]
            )

        return sets

    def handle_message(self, received_json: dict):
        """

        :param received_json:
        :return:
        """
        # Save json file
        with open(LEARNING_SETS_PATH, "w", encoding="UTF-8") as file:
            json.dump(received_json, file, indent="\t")

        with self.cv:
            # Save learning sets
            self.received_data = self.clean_learning_sets(received_json)
            if not AUTO_TEST:
                print("Received learning set")

            # Notify main thread
            self.cv.notify()

    @staticmethod
    def retrieve_classifier_data(model_index) -> cld.ClassifierData:
        with open(VALIDATION_REPORT_PATH, "r", encoding="UTF-8") as file:
            report_json = json.load(file)

        classifier_data = next((item for item in report_json['best_classifiers']
                                if item["classifier_id"] == model_index), None)

        if classifier_data is None or not classifier_data['valid']:
            print("Selected model is not valid")
            return None

        return cld.from_dict(classifier_data)

    def execute_development(self) -> bool:
        # PHASE 1: SETTING NUMBER OF ITERATIONS
        avg_params = self.validation_orchestrator.retrieve_average_parameters()
        self.training_orchestrator.set_parameters(avg_params)

        num_iter_fixed = False
        while not num_iter_fixed:
            num_iter_fixed = self.execute_learning_curve_phase()

        # PHASE 2: GRID SEARCH
        print("Starting Validation...")
        self.validation_orchestrator.grid_search(
            *self.learning_sets["training_set"],
            *self.learning_sets["validation_set"]
        )
        print(f'Please check Validation Report at {VALIDATION_REPORT_PATH}')

        classifier_data = None
        while classifier_data is None:
            selected_model = self.get_user_input(2)
            if selected_model == 0:
                return False
            classifier_data = self.retrieve_classifier_data(selected_model)

        model_path = os.path.join(CLASSIFIER_FOLDER, f'model_{selected_model}.sav')
        classifier = joblib.load(model_path)
        print(f'Model number {selected_model} loaded')

        # PHASE 3: TEST
        print("Starting testing...")
        self.testing_orchestrator.test_classifier(
            classifier,
            classifier_data,
            *self.learning_sets["test_set"]
        )
        print(f'Please check Testing Report at {TESTING_REPORT_PATH}')
        if self.get_user_feedback(3):
            print(f'Sending model_{selected_model} to Production System...')
            self.communication_controller.send_model_to_production(model_path)
            return True
        return False

    def execute_learning_curve_phase(self) -> bool:
        num_iter = {
            "max_iter": self.get_user_input(1)
        }

        print("Generating Learning Curve...")
        self.training_orchestrator.set_parameters(num_iter)
        self.training_orchestrator.generate_learning_curve(
            *self.learning_sets['training_set']
        )

        print(f'Please check Learning Curve at {LEARNING_CURVE_PATH}')
        return self.get_user_feedback(1)

    @staticmethod
    def get_user_input(phase) -> int:
        if phase == 1:
            if not AUTO_TEST:
                num = -1
                while num == -1:
                    user_input = input("Write number of iterations: ")
                    try:
                        num = int(user_input)
                        if num < 100:
                            print("Invalid number: too low")
                            num = -1
                        if num > 2000:
                            print("Invalid number: too high")
                            num = -1
                    except ValueError:
                        print(f'{user_input} is not a number')
                return num
        elif phase == 2:
            if not AUTO_TEST:
                selected_model = -1
                while selected_model == -1:
                    user_input = input("Write index of selected model "
                                       "or 0 to restart development: ")
                    try:
                        selected_model = int(user_input)
                        if selected_model < 0:
                            print("Invalid number: must be non-negative")
                            selected_model = -1
                    except ValueError:
                        print(f'{user_input} is not a number')
                return selected_model


    @staticmethod
    def get_user_feedback(phase) -> bool:
        if phase == 1:
            prompt = "Is number of iterations good? "
        else:
            prompt = "Is test result good? "
        yes = ["y", "yes"]
        no = ["n", "no"]
        if not AUTO_TEST:
            feedback = None
            while feedback is None:
                feedback = input(prompt).lower()
                if feedback in yes:
                    return True
                if feedback in no:
                    return False
                print("Please answer writing 'yes' or 'no'")
                feedback = None

    def run(self):
        if not AUTO_TEST:
            print("Starting REST Server...")

        flask_thread = threading.Thread(
            target=self.communication_controller.start_rest_server,
            args=(LEARNING_SET_SCHEMA_PATH, self.handle_message)
        )
        flask_thread.daemon = True
        flask_thread.start()

        with self.cv:
            while self.received_data is None:
                self.cv.wait()
            self.learning_sets = self.received_data

        print("Starting development...")
        while not self.execute_development():
            print("Restarting development...")

        print("Development completed")
