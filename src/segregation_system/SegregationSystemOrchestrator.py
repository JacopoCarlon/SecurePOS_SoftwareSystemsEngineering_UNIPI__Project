import json
import time

from src.segregation_system.ClassBalancing import CheckClassBalancing, ViewClassBalancing, BalancingReport
from src.segregation_system.InputCoverage import CheckInputCoverage, ViewInputCoverage
from src.segregation_system.PreparedSession import PreparedSessionController

path_config = "src/segregation_system/segregationConfig.json"


class SegregationSystemConfiguration:
    def __init__(self):
        # open configuration file to read all the parameters
        try:
            with open(path_config) as f:
                # load the configuration file
                config = json.load(f)
        except FileNotFoundError:
            print("Configuration file not found")
        except json.JSONDecodeError:
            print("Error decoding JSON file")

        # load the JSON attributes into the object
        self.minimum_session_number = int(config["sessionNumber"])
        self.operation_mode = str(config["operationMode"])


class SegregationSystemOrchestrator:
    # initialize the segregation system
    def __init__(self):
        # load the configuration
        self.segregation_config = SegregationSystemConfiguration()

        # object for the coverage report
        # self.coverage_report = CheckInputCoverage()
        # self.coverage_report_view = ViewInputCoverage(self.coverage_report)

        # object for the prepared sessions
        self.sessions = PreparedSessionController

    def run(self):
        # object for generating the balancing report
        balancing_check = CheckClassBalancing
        # object for generating the coverage report
        coverage_check = CheckInputCoverage

        while True:
            if self.segregation_config.operation_mode == "wait_sessions":
                to_collect = self.segregation_config.minimum_session_number
                collected = self.sessions.sessions_count()

                while collected < to_collect:
                    time.sleep(5)
                    collected = self.sessions.sessions_count()

                # go to the balancing report
                self.segregation_config.operation_mode = "check_balancing"

            if self.segregation_config.operation_mode == "check_balancing":
                balancing_check.set_stats()

                balancing_check_view = ViewClassBalancing(balancing_check)
                balancing_check_view.show_plot()

                self.segregation_config.operation_mode = "generate_balancing_outcome"

            if self.segregation_config.operation_mode == "generate_balancing_outcome":
                balancing_report = BalancingReport()
                # check if the balancing is approved
                if balancing_report.approved:
                    # go to the coverage report
                    self.segregation_config.operation_mode = "check_coverage"
                else:
                    # go back to the wait sessions
                    self.segregation_config.operation_mode = "wait_sessions"

            if self.segregation_config.operation_mode == "check_coverage":
                coverage_check.set_stats()

                coverage_check_view = ViewInputCoverage(coverage_check)
                coverage_check_view.show_plot()


