"""
This module is responsible for checking the input coverage of the dataset.
"""

import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from src.segregation_system.DataExtractor import DataExtractor

outcomes_path = "../../data/segregation_system/outcomes/coverage_outcome.json"
image_path = "../../data/segregation_system/plots/coverage_plot.png"

class CoverageReport:
    """
    Class that holds the outcome of the input coverage check provided
    """
    def __init__(self):
        """
        Constructor for the CoverageReport class.
        """
        try:
            with open(outcomes_path) as f:
                self.outcome = json.load(f)
        except FileNotFoundError:
            print("ERROR> Outcome file not found")
        except json.JSONDecodeError:
            print("ERROR> Error decoding JSON file")

        """
        Load the JSON attributes into the object.
        - approved: bool, whether the input coverage is approved
        - uncovered_features_suggestions: list of str, suggestions for uncovered features
        """
        self.approved = self.outcome["approved"]
        self.uncovered_features_suggestions = self.outcome["uncovered_features_suggestions"]


class CheckInputCoverage:
    """
    Class that checks the input coverage of the dataset.
    """
    def __init__(self):
        """
        Constructor for the CheckInputCoverage class.
        """

        """
        Initialize the statistics attribute.
        - statistics: pd.DataFrame, features of the dataset
        - data_extractor: DataExtractor, object that extracts the features
        """
        self.statistics = {}
        self.data_extractor = DataExtractor()

    def retrieve_features(self):
        """
        Retrieve the features of the dataset.
        """
        data = self.data_extractor.extract_features()

        self.statistics = pd.DataFrame(
            data,
            columns=["longitude", "latitude", "time", "amount", "targetIP", "destIP"]
        )


class ViewInputCoverage:
    """
    Class that visualizes the input coverage of the dataset
    """
    def __init__(self, coverage_report):
        """
        Constructor for the ViewInputCoverage class.
        :param coverage_report: data structure that holds the features for the plot
        """
        self.coverage_report = coverage_report

    def show_plot(self):
        """
        Show the input coverage plot.
        """

        """
        Calculate the number of features and samples in the DataFrame to correctly generate the radar plot.
        """
        df = self.coverage_report.statistics
        num_features = len(df.columns)
        num_samples = len(df)

        """
        Convert degrees to radians for polar plot
        """
        degrees = np.linspace(0, 360, num_features, endpoint=False)
        radians = np.radians(degrees)

        marker = 'o'
        colors = plt.cm.tab20.colors

        """
        Create the plot and configure the axis
        """
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': 'polar'})
        ax.set_title("Input Coverage", fontsize=16, color='darkblue', fontweight='bold')

        """
        Plot each sample as a point in the radar plot
        """
        for i in range(num_samples):
            for j in range(num_features):
                ax.scatter(
                    radians[j], df.iloc[i, j],
                    label=df.columns[j] if i == 0 else "",
                    color=colors[j % len(colors)],
                    marker=marker,
                    s=70,
                    alpha=0.7
                )

        ax.set_xticks(radians)
        ax.set_xticklabels([])
        ax.grid(True, linestyle="--", alpha=0.5, color='gray')

        label_offset = 1.2
        for radian, label in zip(radians, df.columns):
            ax.text(
                radian, label_offset * ax.get_ylim()[1], label,
                ha='center', va='center', fontsize=12, color='black',
                fontweight='bold'
            )

            if np.issubdtype(df[label].dtype, np.number):
                min_val = df[label].min()
                max_val = df[label].max()

                ax.text(
                    radian, 0, f"{min_val:.2f}",
                    ha='center', va='center', fontsize=10, color='blue', fontweight='bold'
                )

                ax.text(
                    radian, ax.get_ylim()[1], f"{max_val:.2f}",
                    ha='center', va='center', fontsize=10, color='red', fontweight='bold'
                )


        """
        Save the plot as a PNG file.
        """
        fig.savefig(image_path, bbox_inches='tight')

