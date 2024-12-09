import json
import os
import time
from src.segregation_system.ClassBalancing import CheckClassBalancing, ViewClassBalancing, BalancingReport
from src.segregation_system.InputCoverage import CheckInputCoverage, ViewInputCoverage
from src.segregation_system.PreparedSession import PreparedSessionController

path_config = "segregationConfig.json"


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
        print("DEBUG> Segregation system initialized: ", self.segregation_config.minimum_session_number, ", ", self.segregation_config.operation_mode)

        # object for the prepared sessions
        self.sessions = PreparedSessionController()
        print("DEBUG> Prepared session controller initialized")

    def run(self):
        # object for generating the balancing report
        balancing_check = CheckClassBalancing()
        print("DEBUG> Balancing check initialized")
        # object for generating the coverage report
        coverage_check = CheckInputCoverage()
        print("DEBUG> Coverage check initialized")

        while True:
            if self.segregation_config.operation_mode == "wait_sessions":
                self.sessions.store("prova.json")
                print("DEBUG> Stored prepared sessions")

                to_collect = self.segregation_config.minimum_session_number
                collected = self.sessions.sessions_count()
                print("DEBUG> Collected sessions: ", collected)

                if collected < to_collect:
                    print("DEBUG> Not enough sessions collected")
                    continue

                # go to the balancing report
                self.segregation_config.operation_mode = "check_balancing"
                print("DEBUG> Operation mode: ", self.segregation_config.operation_mode)

            if self.segregation_config.operation_mode == "check_balancing":
                balancing_check.set_stats()
                print("DEBUG> Set stats for balancing check")

                balancing_check_view = ViewClassBalancing(balancing_check)
                balancing_check_view.show_plot()
                print("DEBUG> Generated plot for balancing check")

                # Prompt user to confirm they've made changes
                while True:
                    user_input = input("Have you modified the required file? (yes/no): ").strip().lower()
                    if user_input == "yes":
                        print("DEBUG> User confirmed file modification.")
                        break
                    elif user_input == "no":
                        print("DEBUG> Waiting for user to modify the file...")
                    else:
                        print("Invalid input. Please enter 'yes' or 'no'.")

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
                return False


