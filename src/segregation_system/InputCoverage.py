import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from src.segregation_system.DataExtractor import DataExtractor

class CoverageReport:
    def __init__(self):
        try:
            with open("coverageOutcome.json") as f:
                self.outcome = json.load(f)
        except FileNotFoundError:
            print("Outcome file not found")
        except json.JSONDecodeError:
            print("Error decoding JSON file")

        self.approved = self.outcome["approved"]
        self.uncovered_features_suggestions = self.outcome["uncovered_features_suggestions"]


class CheckInputCoverage:
    def __init__(self):
        self.statistics = {}
        self.data_extractor = DataExtractor()

    def set_stats(self):
        data = self.data_extractor.extract_features()

        self.statistics = pd.DataFrame(
            data,
            columns=["longitude", "latitude", "time", "amount", "targetIP", "destIP"]
        )

    def retrieve_stats(self):
        return self.statistics


class ViewInputCoverage:
    def __init__(self, coverage_report):
        self.coverage_report = coverage_report

    def show_plot(self):
        df = self.coverage_report.statistics
        print(df)

        num_features = len(df.columns)
        print(f"Number of features: {num_features}")

        num_samples = len(df)
        print(f"Number of samples: {num_samples}")

        # Convert degrees to radians
        degrees = np.linspace(0, 360, num_features, endpoint=False)
        radians = np.radians(degrees)

        # Styling options
        marker = 'o'
        colors = ['r', 'g', 'b', 'c', 'm', 'y']

        # Create polar plot
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # Add scatter points for each feature and sample
        for i in range(num_samples):
            for j in range(num_features):
                ax.scatter(radians[j], df.iloc[i, j],
                           label=df.columns[j], marker=marker,
                           color=colors[j % len(colors)], s=50, alpha=0.7)

        # Show radial lines without angle values
        ax.set_xticks(radians)
        ax.set_xticklabels([])  # Remove angle values
        ax.grid(True, linestyle="--", alpha=0.6)  # Customize grid style

        # Add feature labels and min/max values
        for radian, label in zip(radians, df.columns):
            # Place the feature label outside the plot
            ax.text(radian, ax.get_ylim()[1] + 0.5, label,
                    ha='center', va='center', fontsize=10, color='black',
                    transform=ax.transData)

            # Check if the column contains numeric values
            if np.issubdtype(df[label].dtype, np.number):
                # Get min and max values for the current feature
                min_val = df[label].min()
                max_val = df[label].max()

                # Place min value at the center (origin)
                ax.text(radian, 0, f"{min_val:.2f}",
                        ha='center', va='center', fontsize=8, color='blue',
                        transform=ax.transData)

                # Place max value at the end of the radial line
                ax.text(radian, ax.get_ylim()[1], f"{max_val:.2f}",
                        ha='center', va='center', fontsize=8, color='red',
                        transform=ax.transData)

        plt.title("Input Coverage")
        plt.savefig("coverage_plot.png")