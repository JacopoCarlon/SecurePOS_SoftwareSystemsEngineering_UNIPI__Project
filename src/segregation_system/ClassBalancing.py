"""
This module is responsible for checking the class balancing of the dataset.
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from src.segregation_system.DataExtractor import DataExtractor

path_outcome = "balancingOutcome.json"


class BalancingParameters:
    """
    Class that holds the parameters for the class balancing check.
    """

    def __init__(self):
        """
        Load the parameters from the JSON file.
        """
        try:
            with open("balancingParameters.json") as f:
                self.parameters = json.load(f)
        except FileNotFoundError:
            print("Parameters file not found")
        except json.JSONDecodeError:
            print("Error decoding JSON file")

        """
        Load the JSON attributes into the object.
        # - tolerance: float, percentage of tolerance for the class balancing
        """

        self.tolerance = self.parameters["tolerance"]

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
    """
    Class that prepare the data for the balancing analysis of the risk labels of the dataset.
    """
    def __init__(self):
        self.labels_stat = {}
        self.data_extractor = DataExtractor()

    def set_stats(self):
        """
        Set the statistics of the labels that are shown in the balancing plot.
        """
        labels = self.data_extractor.extract_grouped_labels()

        dictionary = {}

        for row in labels.itertuples(index=False):
            dictionary[row.label] = row.samples

        print("DEBUG> Labels stats: ", dictionary)
        self.labels_stat = dictionary


class ViewClassBalancing:
    """
    Class that shows the plot of the risk class balancing.
    """
    def __init__(self, report):
        self.report = report

    def show_plot(self):
        labels = list(self.report.labels_stat.keys())
        values = list(self.report.labels_stat.values())

        config = BalancingParameters()
        avg = np.mean(np.array(values))
        lower_tolerance = avg - (avg * config.tolerance)
        upper_tolerance = avg + (avg * config.tolerance)

        print("Average: ", avg)
        print("Lower Tolerance: ", lower_tolerance)
        print("Upper Tolerance: ", upper_tolerance)

        # plot the bar chart
        plt.bar(labels, values)
        plt.axhline(y=avg, color='r', linestyle='-', label='Average')
        plt.axhline(y=lower_tolerance, color='g', linestyle='--', label='Lower Tolerance')
        plt.axhline(y=upper_tolerance, color='g', linestyle='--', label='Upper Tolerance')

        plt.xlabel('Classes')
        plt.ylabel('Number of samples')
        plt.title('Risk Level Balancing')

        plt.savefig("balancing_plot.png")
