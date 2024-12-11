import json
import threading
import os
import time
from src.segregation_system.ClassBalancing import CheckClassBalancing, ViewClassBalancing, BalancingReport
from src.segregation_system.InputCoverage import CheckInputCoverage, ViewInputCoverage, CoverageReport
from src.segregation_system.PreparedSession import PreparedSessionController
from src.segregation_system.LearningSetsController import LearningSetsController
from src.comms import ServerREST
from src.segregation_system.JsonIO import FileReceptionAPI
from src.db_sqlite3 import DatabaseController

path_config = "segregationConfig.json"

"""
Class that holds the configuration of the segregation system. It reads the configuration file and loads the parameters
into the object. The parameters are:
- minimum_session_number: the minimum number of sessions to collect before starting the segregation process
- operation_mode: the current operation mode of the segregation system
"""
class SegregationSystemConfiguration:
    def __init__(self):
        # open configuration file to read all the parameters
        try:
            with open(path_config) as f:
                # load the configuration file
                config = json.load(f)
                # load the JSON attributes into the object
                self.minimum_session_number = int(config["sessionNumber"])
                self.operation_mode = str(config["operationMode"])
                print("DEBUG> Minimum session number: ", self.minimum_session_number)
                print("DEBUG> Operation mode: ", self.operation_mode)
        except FileNotFoundError:
            print("Configuration file not found")
        except json.JSONDecodeError:
            print("Error decoding JSON file")


class SegregationSystemOrchestrator:
    # initialize the segregation system
    def __init__(self):
        # load the configuration
        self.segregation_config = SegregationSystemConfiguration()
        self.db = DatabaseController("database.db")
        self.last_file_mod_time = None  # Track the last modification time of the JSON file

        # object for the prepared sessions
        self.sessions = PreparedSessionController()

        # Start REST server in a separate thread
        self.rest_server = ServerREST()
        self.rest_server.api.add_resource(
            FileReceptionAPI,
            '/upload',
            resource_class_kwargs={'filename': 'prova.json'}
        )
        self.server_thread = threading.Thread(
            target=self.rest_server.run,
            kwargs={'host': '0.0.0.0', 'port': 5000, 'debug': False}
        )
        self.server_thread.daemon = True
        self.server_thread.start()

    def receive(self):
        # Wait for file to appear in the data folder
        filepath = "prova.json"
        while not os.path.exists(filepath):
            print("DEBUG> Waiting for file reception...")
            time.sleep(5)
        print("DEBUG> File received: ", filepath)
        return filepath

    def run(self):
        # object for generating the balancing report
        balancing_check = CheckClassBalancing()
        # object for generating the coverage report
        coverage_check = CheckInputCoverage()

        while True:
            if self.segregation_config.operation_mode == "wait_sessions":
                received_file = self.receive()

                self.sessions.store(received_file)

                # Start with the previous limit as the base required sessions
                to_collect = self.segregation_config.minimum_session_number
                required_sessions = to_collect  # Initialize with the previous limit
                print("DEBUG> Required sessions: ", required_sessions)

                # Check if we are re-entering due to a negative outcome
                json_file_path = "balancingOutcome.json"  # Or "coverageOutcome.json" based on context
                if os.path.exists(json_file_path):
                    try:
                        with open(json_file_path, "r") as json_file:
                            outcome_data = json.load(json_file)

                        unbalanced_classes = outcome_data["unbalanced_classes"]
                        print(f"DEBUG> Unbalanced classes: {unbalanced_classes}")

                        # Calculate the additional sessions required based on the outcome
                        additional_sessions = sum(unbalanced_classes.values())

                        # Update to_collect with the sum of these values
                        to_collect += additional_sessions
                        print(f"DEBUG> Added {additional_sessions} sessions from unbalanced_classes")

                        print(f"DEBUG> Adjusted required sessions based on outcome: {to_collect}")
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"ERROR> Failed to read or parse the outcome file: {e}")

                collected = self.sessions.sessions_count()

                if collected < to_collect:
                    print(f"DEBUG> Not enough sessions collected. Collected: {collected}, Required: {to_collect}")
                    time.sleep(5)
                    continue

                # Go to the balancing report
                self.segregation_config.operation_mode = "check_balancing"
                print("DEBUG> Operation mode: ", self.segregation_config.operation_mode)

            if self.segregation_config.operation_mode == "check_balancing":
                balancing_check.set_stats()
                print("DEBUG> Set stats for balancing check")

                balancing_check_view = ViewClassBalancing(balancing_check)
                balancing_check_view.show_plot()
                print("DEBUG> Generated plot for balancing check")

                json_file_path = "balancingOutcome.json"

                # Prompt user to confirm they've made changes
                while True:
                    try:
                        # Prompt user to input the outcome
                        user_input = input("Is the balancing correct? (yes/no): ").strip().lower()

                        if user_input == "yes":
                            approved = True
                            print("DEBUG> User approved balancing.")
                            # Write the user's decision to the JSON file
                            data = {
                                "approved": approved,
                                "unbalanced_classes": {
                                    "normal": 0,
                                    "moderate": 0,
                                    "high": 0
                                }
                            }

                            with open(json_file_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)

                            break
                        elif user_input == "no":
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

                            with open(json_file_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)
                            print("DEBUG> User disapproved balancing.")
                            print("DEBUG> Balancing not approved. Waiting for user to modify the JSON file...")

                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                            continue

                    except Exception as e:
                        print(f"ERROR> An error occurred: {e}")

                self.segregation_config.operation_mode = "generate_balancing_outcome"
                print("DEBUG> Operation mode: ", self.segregation_config.operation_mode)

            if self.segregation_config.operation_mode == "generate_balancing_outcome":
                balancing_report = BalancingReport()
                print("DEBUG> Balancing report generated")
                print("DEBUG> Balancing approved: ", balancing_report.approved)
                print("DEBUG> Unbalanced classes: ", balancing_report.unbalanced_classes)
                # check if the balancing is approved
                if balancing_report.approved:
                    # go to the coverage report
                    print("DEBUG> Balancing approved")
                    self.segregation_config.operation_mode = "check_coverage"
                else:
                    # send the balancing outcome
                    print("DEBUG> Balancing not approved")
                    # go back to the wait sessions
                    self.segregation_config.operation_mode = "wait_sessions"

            if self.segregation_config.operation_mode == "check_coverage":
                coverage_check.set_stats()
                print("DEBUG> Set stats for coverage check")

                coverage_check_view = ViewInputCoverage(coverage_check)
                coverage_check_view.show_plot()
                print("DEBUG> Generated plot for coverage check")

                json_file_path = "coverageOutcome.json"

                while True:
                    try:
                        # Prompt user to input the outcome
                        user_input = input("Is the coverage correct? (yes/no): ").strip().lower()

                        if user_input == "yes":
                            approved = True
                            print("DEBUG> User approved coverage.")

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

                            with open(json_file_path, "w") as json_file:
                                json.dump(data, json_file, indent=4)
                        elif user_input == "no":
                            approved = False
                            print("DEBUG> User disapproved coverage.")
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                            continue

                        if approved:
                            print("DEBUG> Coverage approved in JSON file.")
                            break
                        else:
                            print("DEBUG> Coverage not approved. Waiting for user to modify the JSON file...")

                            while True:
                                modification_input = input(
                                    "Have you modified the coverage file? (yes/no): ").strip().lower()
                                if modification_input == "yes":
                                    print("DEBUG> User confirmed file modification.")
                                    break
                                elif modification_input == "no":
                                    print("DEBUG> Waiting for user to modify the file...")
                                    time.sleep(2)
                                else:
                                    print("Invalid input. Please enter 'yes' or 'no'.")

                    except Exception as e:
                        print(f"ERROR> An error occurred: {e}")

                self.segregation_config.operation_mode = "generate_coverage_outcome"
                print("DEBUG> Operation mode: ", self.segregation_config.operation_mode)

            if self.segregation_config.operation_mode == "generate_coverage_outcome":
                coverage_report = CoverageReport()
                print("DEBUG> Coverage report generated")
                print("DEBUG> Coverage approved: ", coverage_report.approved)
                print("DEBUG> Uncovered features: ", coverage_report.uncovered_features_suggestions)

                # check if the coverage is approved
                if coverage_report.approved:
                    # go to the wait sessions
                    print("DEBUG> Coverage approved")
                    self.segregation_config.operation_mode = "generate_sets"
                else:
                    # send the coverage outcome
                    print("DEBUG> Coverage not approved")
                    # go back to the wait sessions
                    self.segregation_config.operation_mode = "wait_sessions"

            if self.segregation_config.operation_mode == "generate_sets":
                learning_sets_controller = LearningSetsController()
                learning_sets_controller.save_sets()
                print("DEBUG> Learning sets generated and saved")

                learning_sets_controller.send_learning_sets("all_sets.json")
                print("DEBUG> Learning sets sent")

                self.db.drop_table("prepared_sessions")

                return False


