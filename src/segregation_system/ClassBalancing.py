"""
This module is responsible for checking the class balancing of the dataset.
"""
import json

path_outcome = "data/balancing_outcome.json"


class BalancingReport:
    """
    Class that holds the outcome of the class balancing check provided
    by the Data Analyst.
    """

    def __init__(self):
        """
        Load the outcome from the JSON file.
        """
        try:
            with open(path_outcome) as f:
                self.outcome = json.load(f)
        except FileNotFoundError:
            print("Outcome file not found")
        except json.JSONDecodeError:
            print("Error decoding JSON file")


        """
        Load the JSON attributes into the object.
        # - approved: boolean, whether the class balancing is approved
        # - unbalanced_classes: list of classes that are unbalanced and how many
        # samples the Data Analyst wants
        """

        self.approved = self.outcome["approved"]
        self.unbalanced_classes = self.outcome["unbalanced_classes"]

class CheckClassBalancing:
    def __init__(self):
        pass

    def retrieve_labels(self):
        pass


class ViewClassBalancing:
    def __init__(self, report):
        pass

    def show_plot(self):
        pass
