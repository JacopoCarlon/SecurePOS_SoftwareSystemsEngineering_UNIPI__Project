import os
from utility import data_folder
from development_system.dev_sys_communication_controller import DevSysCommunicationController

COMMUNICATION_CONFIG_PATH = os.path.join(data_folder, "development_system_data/dev_sys_comms_configuration.json")


class DevelopmentSystemOrchestrator:
    """
    Orchestrator class for development system
    """

    def __init__(self):
        self.communication_controller = DevSysCommunicationController(COMMUNICATION_CONFIG_PATH)

    def run(self):
        """
        Main flow of execution
        """
