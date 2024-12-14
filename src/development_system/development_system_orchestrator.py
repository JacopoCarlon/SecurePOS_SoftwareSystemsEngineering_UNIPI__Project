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
from utility.json_validation import validate_json
from development_system.development_system_status import DevelopmentSystemStatus
from development_system.dev_sys_communication_controller import DevSysCommunicationController
from development_system.training_orchestrator import TrainingOrchestrator
from development_system.validation_orchestrator import ValidationOrchestrator
from development_system.testing_orchestrator import TestingOrchestrator

# Json Schemas
COMM_CONFIG_SCHEMA_PATH = "development_system/json_schemas/comm_config_schema.json"
LEARNING_SET_SCHEMA_PATH = "development_system/json_schemas/learning_set_schema.json"
VAL_CONFIG_SCHEMA_PATH = "development_system/json_schemas/val_config_schema.json"
TEST_CONFIG_SCHEMA_PATH = "development_system/json_schemas/test_config_schema.json"

# Configuration files
COMMUNICATION_CONFIG_PATH = os.path.join(data_folder, "development_system/configs/communications_configuration.json")
VALIDATION_CONFIG_PATH = os.path.join(data_folder, "development_system/configs/validation_configuration.json")
TESTING_CONFIG_PATH = os.path.join(data_folder, "development_system/configs/testing_configuration.json")
USER_INPUT_PATH = os.path.join(data_folder, "development_system/configs/user_input.json")

# Status files
STATUS_FILE_PATH = os.path.join(data_folder, "development_system/internal/status.json")

# Learning sets file
RECEIVED_DATA_PATH = os.path.join(data_folder, "development_system/internal/received_data.json")
LEARNING_SETS_PATH = os.path.join(data_folder, "development_system/internal/learning_sets.json")

# Classifier models folder
CLASSIFIER_FOLDER = os.path.join(data_folder, "development_system/classifiers/")

# Report files
LEARNING_CURVE_PATH = os.path.join(data_folder, "development_system/reports/learning_curve.png")
VALIDATION_REPORT_PATH = os.path.join(data_folder, "development_system/reports/validation_report.json")
TESTING_REPORT_PATH = os.path.join(data_folder, "development_system/reports/testing_report.json")


class DevelopmentSystemOrchestrator:
    """
    Orchestrator class for development system
    """
    def __init__(self):
        """
        Initialization of System Orchestrator
        """
        # Condition Variable for waiting learning sets
        self.cv = threading.Condition()

        # System status
        self.status = DevelopmentSystemStatus(
            STATUS_FILE_PATH
        )

        # Communication controller
        self.communication_controller = DevSysCommunicationController(
            COMMUNICATION_CONFIG_PATH,
            COMM_CONFIG_SCHEMA_PATH
        )

        # Learning sets
        self.learning_sets = None

    @staticmethod
    def ip_to_float(ip_string):
        return float(int(ipaddress.ip_address(ip_string)))\
               / float(int(ipaddress.ip_address("255.255.255.255")))

    def handle_message(self, received_json: dict):
        """
        Handler for receiving learning sets
        :param received_json: received data
        :return:
        """
        with self.cv:
            # dumps received data
            with open(RECEIVED_DATA_PATH, "w", encoding="UTF-8") as file:
                json.dump(received_json, file, indent="\t")
            print("Received learning set")

            # Notify main thread
            self.status.update_status({"phase": "Ready"})
            self.cv.notify()

    @staticmethod
    def retrieve_classifier_data(model_index: int) -> dict:
        """
        Open validation report to retrieve information about a classifier
        :param model_index: index of desired classifier
        :return: a dictionary containing the information from the report
        """
        with open(VALIDATION_REPORT_PATH, "r", encoding="UTF-8") as file:
            report_json = json.load(file)

        # search for specified index
        classifier_data = next((item for item in report_json['best_classifiers']
                                if item["index"] == model_index), None)

        if classifier_data is None or not classifier_data['valid']:
            return None

        return classifier_data

    def reset_user_input(self):
        """
        Resets file used for getting user input.
        Previous phases input is maintained.
        :return:
        """
        phase = self.status.get_phase()
        dummy_input = {
            "max_iter": self.status.get_max_iter(),
            "good_max_iter": phase not in ["Ready", "LearningCurve"],
            "best_model": self.status.get_best_classifier_id(),
            "approved": False
        }

        with open(USER_INPUT_PATH, "w", encoding="UTF-8") as file:
            json.dump(dummy_input, file, indent='\t')

    def execute_development(self):
        """
        Main flow of execution as a state machine
        :return:
        """
        # PHASE 1: SETTING NUMBER OF ITERATIONS
        # 1.1: set average hyper_parameters
        if self.status.get_phase() == "Ready":
            # retrieve average hyper_parameters from Validation Orchestrator
            validation_orchestrator = ValidationOrchestrator(
                VALIDATION_CONFIG_PATH,
                VAL_CONFIG_SCHEMA_PATH,
                CLASSIFIER_FOLDER,
                VALIDATION_REPORT_PATH,
                TrainingOrchestrator()
            )
            avg_params = validation_orchestrator.retrieve_average_parameters()
            print(f'Average hyperparameters set:\n{avg_params}')

            # update status
            self.status.update_status({
                "avg_params":   avg_params,
                "phase":        "LearningCurve"
            })
            self.reset_user_input()
            print(f'Please write number of iterations in {USER_INPUT_PATH}')
            exit(0)

        # 1.2: generate learning curve
        elif self.status.get_phase() == "LearningCurve":
            # get input from user
            user_input = self.get_user_input()

            # Learning curve not present OR bad number of iterations
            if self.status.first_iter() or not user_input['good_max_iter']:
                # save number of iterations
                self.status.update_status({"max_iter": user_input['max_iter']})
                print(f'Generating Learning Curve with maximum {user_input["max_iter"]} iterations')

                # generate curve
                to = TrainingOrchestrator()
                to.set_parameters(self.status.get_training_params())
                to.generate_learning_curve(
                    self.learning_sets['training_set']['features'],
                    self.learning_sets['training_set']['labels'],
                    LEARNING_CURVE_PATH
                )

                # ask for user input
                self.reset_user_input()
                print(f'Please check Learning Curve at {LEARNING_CURVE_PATH}')
                exit(0)

            # Good number of iterations, proceed to validation
            else:
                print(f'Good number of iterations: {self.status.get_max_iter()}')
                self.status.update_status({"phase": "Validation"})
                self.execute_development()

        # PHASE 2: VALIDATION
        # 2.1: Grid Search
        elif self.status.get_phase() == "Validation":
            print("Starting Validation...")

            # Create training orchestrator and set max_iter
            training_orchestrator = TrainingOrchestrator()
            training_orchestrator.set_parameters({
                "max_iter": self.status.get_max_iter()
            })

            # Create validation orchestrator
            validation_orchestrator = ValidationOrchestrator(
                VALIDATION_CONFIG_PATH,
                VAL_CONFIG_SCHEMA_PATH,
                CLASSIFIER_FOLDER,
                VALIDATION_REPORT_PATH,
                training_orchestrator
            )
            # Grid search
            validation_orchestrator.grid_search(
                self.learning_sets['training_set']['features'],
                self.learning_sets['training_set']['labels'],
                self.learning_sets['validation_set']['features'],
                self.learning_sets['validation_set']['labels']
            )

            # Ask user to check the report
            print(f'Please check Validation Report at {VALIDATION_REPORT_PATH}')
            print(f'Please write best_model in {USER_INPUT_PATH}')
            print("Choose 0 as best model to restart development")
            self.status.update_status({'phase': "ValidationReport"})
            self.reset_user_input()
            exit(0)

        # 2.2: Select best model
        elif self.status.get_phase() == "ValidationReport":
            best_model_index = self.get_user_input()["best_model"]
            print(f'User chose model number {best_model_index}')

            # All rejected
            if best_model_index == 0:
                print("Validation rejected, restarting development...")
                # Restart Development process
                self.status.retry()
                self.execute_development()

            print("Retrieving classifier...")
            classifier_data = self.retrieve_classifier_data(best_model_index)

            # User chose invalid classifier
            if classifier_data is None:
                print("Selected model is not valid")
                exit(0)
            else:
                # Proceed to testing
                print(f'Model number {best_model_index}:\n{classifier_data}')
                self.status.update_status({
                    "phase": "Testing",
                    "best_classifier_data": classifier_data
                })
                self.execute_development()

        # PHASE 3: TESTING
        elif self.status.get_phase() == "Testing":
            print("Starting testing...")
            # prepare classifier
            best_classifier_data = self.status.get_best_classifier_data()
            cl_id = best_classifier_data['index']
            model_path = os.path.join(CLASSIFIER_FOLDER, f'model_{cl_id}.sav')
            model = joblib.load(model_path)

            # prepare Testing Orchestrator
            testing_orchestrator = TestingOrchestrator(
                TESTING_CONFIG_PATH,
                TEST_CONFIG_SCHEMA_PATH,
                TESTING_REPORT_PATH
            )

            # execute test
            testing_orchestrator.test_classifier(
                model,
                best_classifier_data,
                self.learning_sets['test_set']['features'],
                self.learning_sets['test_set']['labels'],
            )

            # update status
            self.status.update_status(
                {"phase": "Results"}
            )
            self.reset_user_input()
            print("Testing ended")
            print(f'Please check Testing Report at {TESTING_REPORT_PATH}')
            exit(0)

        # PHASE 4: RESULTS
        elif self.status.get_phase() == "Results":
            if self.get_user_input()["approved"]:
                print("Test Report is approved. Sending classifier to Production System...")
                # Send classifier
                best_classifier_data = self.status.get_best_classifier_data()
                cl_id = best_classifier_data['index']
                model_path = os.path.join(CLASSIFIER_FOLDER, f'model_{cl_id}.sav')
                self.communication_controller.send_model_to_production(model_path)

            else:
                # Failure
                print("Test Report is rejected. Development Failed.")

            # Reset development system
            self.status.reset()

    def get_user_input(self) -> dict:
        """
        Looks for user input in dedicated file.
        :return: dictionary of inputs
        """
        # dynamic schema for validation
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Root",
            "type": "object",
            "properties": {},
            "required": []
        }
        if self.status.get_phase() == "LearningCurve":
            schema["required"] = ["max_iter", "good_max_iter"]
            schema["properties"] = {
                "max_iter": {"type": "integer", "minimum": 100, "maximum": 2000},
                "good_max_iter": {"type": "boolean"}
            }
        elif self.status.get_phase() == "ValidationReport":
            schema["required"] = ["best_model"]
            schema["properties"] = {
                "best_model": {"type": "integer", "minimum": 0}
            }
        elif self.status.get_phase() == "Results":
            schema["required"] = ["approved"]
            schema["properties"] = {
                "approved": {"type": "boolean"}
            }

        try:
            with open(USER_INPUT_PATH, "r", encoding="UTF-8") as file:
                user_input = json.load(file)

            if not validate_json(user_input, schema):
                exit(0)

            return user_input

        except FileNotFoundError:
            print(f'ERROR: File {USER_INPUT_PATH} is needed for user input')
            exit(0)

    def run(self):
        """
        Starting point of application
        :return:
        """
        # PHASE 0: wait for a learning set
        if self.status.get_phase() == "Waiting":
            print("Starting REST Server...")
            flask_thread = threading.Thread(
                target=self.communication_controller.start_rest_server,
                args=(LEARNING_SET_SCHEMA_PATH, self.handle_message)
            )
            flask_thread.daemon = True
            flask_thread.start()
            print("Waiting for data...")

            with self.cv:
                while self.status.get_phase() == "Waiting":
                    self.cv.wait()
                # Save learning set
                os.replace(RECEIVED_DATA_PATH, LEARNING_SETS_PATH)

        # load learning_sets
        with open(LEARNING_SETS_PATH, "r", encoding="UTF-8") as file:
            self.learning_sets = json.load(file)

        # Start main flow of execution
        self.execute_development()

        # End of Development Process
        print("Development completed")
