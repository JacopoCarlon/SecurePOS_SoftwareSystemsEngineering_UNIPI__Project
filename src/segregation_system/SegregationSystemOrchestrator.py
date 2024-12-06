import json
import time

from src.segregation_system.ClassBalancing import CheckClassBalancing, ViewClassBalancing
# from src.segregation_system.src.InputCoverage import CheckInputCoverage, ViewInputCoverage
from src.segregation_system.PreparedSession import PreparedSessionController

path_config = "src/segregation_system/data/segregationConfig.json"


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
        self.minimum_session_number = int(config["session_number"])
        self.operation_mode = str(config["operation_mode"])


class SegregationSystemOrchestrator:
    # initialize the segregation system
    def __init__(self):
        # load the configuration
        self.segregation_config = SegregationSystemConfiguration()

        # object for the balancing report
        self.balancing_report = CheckClassBalancing
        self.balancing_report_view = ViewClassBalancing(self.balancing_report)

        # object for the coverage report
        # self.coverage_report = CheckInputCoverage()
        # self.coverage_report_view = ViewInputCoverage(self.coverage_report)

        # object for the prepared sessions
        self.sessions = PreparedSessionController

    def run(self):
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
                self.balancing_report.retrieve_labels()
                self.balancing_report_view.show_plot()

                self.segregation_config.operation_mode = "generate_balancing_outcome"

            if self.segregation_config.operation_mode == "generate_balancing_outcome":
                # generate the balancing outcome
                pass

