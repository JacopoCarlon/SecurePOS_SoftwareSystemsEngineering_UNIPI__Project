"""
This module is responsible for orchestrating the segregation system.
It receives the prepared sessions, checks the risk class balancing and the feature coverage, generates the learning sets and sends them to the development system.
It also starts the REST server to receive the prepared sessions from the preparation system.
"""

import json
import threading
import os
import time
from typing import Callable

from src.segregation_system.JsonIO import ReceiveJsonApi
from src.segregation_system.ClassBalancing import CheckClassBalancing, ViewClassBalancing, BalancingReport
from src.segregation_system.InputCoverage import CheckInputCoverage, ViewInputCoverage, CoverageReport
from src.segregation_system.PreparedSession import PreparedSessionController
from src.segregation_system.LearningSetsController import LearningSetsController
from src.comms import ServerREST
from src.db_sqlite3 import DatabaseController
from src.segregation_system.CommunicationController import CommunicationController

config_path = "../../data/segregation_system/config/segregation_config.json"
json_balancing_path = "../../data/segregation_system/outcomes/balancing_outcome.json"
json_coverage_path = "../../data/segregation_system/outcomes/coverage_outcome.json"
set_path = "../../data/segregation_system/sets/all_sets.json"
file_path = "../../data/segregation_system/input/prepared_sessions.json"


class SegregationSystemConfiguration:
    """
    Class that holds the configuration of the segregation system. It reads the configuration file and loads the parameters
    into the object. The parameters are:
    - minimum_session_number: the minimum number of sessions to collect before starting the segregation process
    - operation_mode: the current operation mode of the segregation system
    """
    def __init__(self):
        """
        Constructor of the SegregationSystemConfiguration class. It reads the configuration file and loads the parameters
        into the object.
        """
        try:
            with open(config_path) as f:
                """
                Open the configuration file
                """
                config = json.load(f)

                """
                Load the parameters into the object
                """
                self.minimum_session_number = int(config["sessionNumber"])
                self.operation_mode = str(config["operationMode"])
                self.development_system_endpoint = str(config["developmentSystemEndpoint"])
        except FileNotFoundError:
            """
            If the configuration file is not found, print an error message
            """
            print("ERROR> Configuration file not found")
        except json.JSONDecodeError:
            """
            If the configuration file is not a valid JSON file, print an error message
            """
            print("ERROR> Error decoding JSON file")


class SegregationSystemOrchestrator:
    """
    Class that orchestrates the segregation system. It receives the prepared sessions, checks the risk class balancing and the feature
    coverage, generates the learning sets and sends them to the development system. It also starts the REST server to receive
    the prepared sessions from the preparation system.
    """
    def __init__(self):
        """
        Constructor of the SegregationSystemOrchestrator class. It initializes the configuration object, the database controller,
        the prepared session controller and the REST server.
        """

        """
        Load the configuration object
        """
        self.segregation_config = SegregationSystemConfiguration()

        """
        Initialize the database controller
        """
        self.db = DatabaseController("database.db")

        """
        Initialize the prepared session controller
        """
        self.sessions = PreparedSessionController()

        self.communication_controller = CommunicationController()

    def start_rest_server(self, json_schema_path: dict, handler: Callable[[dict], None]) -> None:
        """
        Starts rest server for json file reception
        :param json_schema_path: schema for json validation
        :param handler: handler function
        :return:
        """
        self.server = ServerREST()
        self.server.api.add_resource(
            ReceiveJsonApi,
            "/",
            resource_class_kwargs={
                'json_schema_path': json_schema_path,
                'handler': handler
            })
        self.server.run(host="192.168.159.110", port=5000, debug=False)

    def receive(self, received_json: dict):
        """
        Method that receives the prepared sessions from the preparation system. It waits for the file to appear in the data folder
        and then stores the sessions in the database.
        :return: file path of the received file
        """

        with open(file_path, "w") as f:
            json.dump(received_json, f, indent=4)

    def run(self):
        """
        Method that starts the segregation process. It waits for the minimum number of sessions to be collected, then checks the
        risk class balancing and the feature coverage. If the balancing and coverage are approved, it generates the learning sets
        and sends them to the development system.
        """

        """
        Start the REST server in a separate thread
        """
        flask_thread = threading.Thread(
            target=self.communication_controller.start_server,
            args=(file_path, self.receive)
        )
        flask_thread.daemon = True
        flask_thread.start()

        """
        Initialize the class balancing check
        """
        balancing_check = CheckClassBalancing()

        """
        Initialize the input coverage check
        """
        coverage_check = CheckInputCoverage()

        """
        The system is in a loop until the learning sets are generated and sent to the development system
        """
        while True:
            """
            The system starts by waiting for the minimum number of sessions to be collected
            """
            if self.segregation_config.operation_mode == "wait_sessions":
                """
                Receive the prepared sessions file from the preparation system and store the sessions in the database
                """
                while not os.path.exists(file_path):
                    time.sleep(5)

                with open(file_path) as f:
                    received_file = json.load(f)
                self.sessions.store(received_file)

                """
                Check if the minimum number of sessions has been collected
                """
                to_collect = self.segregation_config.minimum_session_number
                collected = self.sessions.sessions_count()

                if collected < to_collect:
                    print(f"Not enough sessions collected. Collected: {collected}, Required: {to_collect}")
                    time.sleep(5)
                    continue

                """
                Go to the class balancing check
                """
                self.segregation_config.operation_mode = "check_balancing"

            """
            The system checks the risk class balancing by generating a plot of the risk classes and prompting the user to approve
            the balancing. If the balancing is approved, the system goes to the feature coverage check. If the balancing is not
            approved, the system goes back to the wait sessions and the data analyst modify the json file with the number of
            samples he needs.
            """
            if self.segregation_config.operation_mode == "check_balancing":
                """
                Retrieve the labels of the prepared sessions from the database
                """
                balancing_check.retrieve_labels()

                """
                Initialize the object to view the class balancing check and generate the plot
                """
                balancing_check_view = ViewClassBalancing(balancing_check)
                balancing_check_view.show_plot()
                print("Generated plot for class balancing check")

                """
                The Data Analyst is prompted to approve the balancing and update the json file that contain
                the outcome to send to the configuration system.
                """
                while True:
                    try:
                        """
                        Data Analyst is prompted to approve the balancing
                        """
                        user_input = input("Is the balancing correct? (yes/no): ").strip().lower()

                        if user_input == "yes":
                            """
                            If the balancing is approved, the json file is updated with the approved flag set to True
                            """
                            approved = True

                            data = {
                                "approved": approved,
                                "unbalanced_classes": {
                                    "normal": 0,
                                    "moderate": 0,
                                    "high": 0
                                }
                            }

                            with open(json_balancing_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)

                            break
                        elif user_input == "no":
                            """
                            If the balancing is not approved, the json file is updated with the approved flag set to False
                            and the number of samples needed for each class is prompted to the Data Analyst
                            """
                            approved = False

                            normal = input("How many \"normal\" samples do you need? ").strip().lower()
                            moderate = input("How many \"moderate\" samples do you need? ").strip().lower()
                            high = input("How many \"high\" samples do you need? ").strip().lower()

                            data = {
                                "approved": approved,
                                "unbalanced_classes": {
                                    "normal": int(normal),
                                    "moderate": int(moderate),
                                    "high": int(high)
                                }
                            }

                            with open(json_balancing_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)

                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                            continue

                    except Exception as e:
                        print(f"ERROR> An error occurred: {e}")

                """
                Go to the generate balancing outcome mode that checks the outcome of the class balancing
                """
                self.segregation_config.operation_mode = "generate_balancing_outcome"

            """
            The outcome of the balancing plot is checked to see if the balancing is approved. If the balancing is approved, the
            system goes to the feature coverage check. If the balancing is not approved, the system goes back to the wait sessions
            """
            if self.segregation_config.operation_mode == "generate_balancing_outcome":
                """
                Initialize the object to check the balancing outcome
                """
                balancing_report = BalancingReport()

                if balancing_report.approved:
                    self.segregation_config.operation_mode = "check_coverage"
                else:
                    # send the balancing outcome

                    self.segregation_config.operation_mode = "wait_sessions"

            """
            The system checks the feature coverage by generating a plot of the features and prompting the Data Analyst to approve the
            coverage. If the coverage is approved, the system generates the learning sets and sends them to the development system.
            If the coverage is not approved, the system goes back to the wait sessions and the Data Analyst modifies the json file
            with some suggestions about the features that are not well covered.
            """
            if self.segregation_config.operation_mode == "check_coverage":
                """
                Retrieve the features of the prepared sessions from the database
                """
                coverage_check.retrieve_features()

                """ 
                Initialize the object to view the input coverage check and generate the plot
                """
                coverage_check_view = ViewInputCoverage(coverage_check)
                coverage_check_view.show_plot()

                """
                The Data Analyst is prompted to approve the coverage and update the json file that contain the outcome to send to
                the configuration system.
                """
                while True:
                    try:
                        """
                        Data Analyst is prompted to approve the coverage
                        """
                        user_input = input("Is the coverage correct? (yes/no): ").strip().lower()

                        if user_input == "yes":
                            """
                            If the coverage is approved, the json file is updated with the approved flag set to True
                            """
                            approved = True

                            data = {
                                "approved": approved,
                                "uncovered_features_suggestions": {
                                    "median_longitude": "",
                                    "median_latitude": "",
                                    "mean_diff_time": "",
                                    "mean_diff_amount": "",
                                    "median_targetIP": "",
                                    "median_destIP": ""
                                }
                            }

                            with open(json_coverage_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)

                            break
                        elif user_input == "no":
                            approved = False

                            median_longitude = input("Enter a suggestion for the median longitude: ").strip().lower()
                            median_latitude = input("Enter a suggestion for the median latitude: ").strip().lower()
                            mean_diff_time = input("Enter a suggestion for the mean difference in time: ").strip().lower()
                            mean_diff_amount = input("Enter a suggestion for the mean difference in amount: ").strip().lower()
                            median_target_ip = input("Enter a suggestion for the median target IP: ").strip().lower()
                            median_dest_ip = input("Enter a suggestion for the median destination IP: ").strip().lower()

                            data = {
                                "approved": approved,
                                "uncovered_features_suggestions": {
                                    "median_longitude": median_longitude,
                                    "median_latitude": median_latitude,
                                    "mean_diff_time": mean_diff_time,
                                    "mean_diff_amount": mean_diff_amount,
                                    "median_targetIP": median_target_ip,
                                    "median_destIP": median_dest_ip
                                }
                            }

                            with open(json_coverage_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)

                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                            continue

                    except Exception as e:
                        print(f"ERROR> An error occurred: {e}")

                """
                Go to the generate coverage outcome mode that checks the outcome of the feature coverage
                """
                self.segregation_config.operation_mode = "generate_coverage_outcome"

            """
            The outcome of the coverage plot is checked to see if the coverage is approved. If the coverage is approved, the system
            generates the learning sets and sends them to the development system. If the coverage is not approved, the system goes
            back to the wait sessions.
            """
            if self.segregation_config.operation_mode == "generate_coverage_outcome":
                """
                Initialize the object to check the coverage outcome
                """
                coverage_report = CoverageReport()

                if coverage_report.approved:
                    self.segregation_config.operation_mode = "generate_sets"
                else:
                    # send the coverage outcome

                    self.segregation_config.operation_mode = "wait_sessions"

            """
            The system generates the learning sets and sends them to the development system. It also drops the table of prepared
            sessions in the database.
            """
            if self.segregation_config.operation_mode == "generate_sets":
                """
                Initialize the learning sets controller and generate the learning sets
                """
                learning_sets_controller = LearningSetsController()
                learning_sets_controller.save_sets()

                """
                Send the learning sets to the development system
                """
                self.communication_controller.send_learning_sets(set_path)

                """
                Drop the table of prepared sessions in the database
                """
                self.db.drop_table("prepared_sessions")

                return False
