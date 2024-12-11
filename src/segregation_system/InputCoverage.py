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
        # Retrieve the coverage report statistics
        df = self.coverage_report.statistics
        num_features = len(df.columns)
        num_samples = len(df)
        print("Coverage Report DataFrame:")
        print(df)
        print(f"Number of features: {num_features}")
        print(f"Number of samples: {num_samples}")

        # Convert degrees to radians for polar plot
        degrees = np.linspace(0, 360, num_features, endpoint=False)
        radians = np.radians(degrees)

        # Styling options for better readability
        marker = 'o'
        colors = plt.cm.tab20.colors  # Use a color map for better contrast

        # Create the polar plot
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': 'polar'})
        ax.set_title("Input Coverage", fontsize=16, color='darkblue', fontweight='bold')

        # Plot each sample in the DataFrame
        for i in range(num_samples):
            for j in range(num_features):
                ax.scatter(
                    radians[j], df.iloc[i, j],
                    label=df.columns[j] if i == 0 else "",  # Only label the first occurrence of each feature
                    color=colors[j % len(colors)],  # Use color map for variety
                    marker=marker,
                    s=70,  # Adjust the size of the markers for better visibility
                    alpha=0.7  # Set transparency for overlapping points
                )

        # Configure radial axis labels and grid
        ax.set_xticks(radians)
        ax.set_xticklabels([])  # Hide angle labels to avoid clutter
        ax.grid(True, linestyle="--", alpha=0.5, color='gray')  # Adjust grid style for better contrast

        # Add feature labels and min/max values
        label_offset = 1.2  # Offset for placing the labels outside the plot
        for radian, label in zip(radians, df.columns):
            # Add the feature label with styling, slightly moved out from the circle
            ax.text(
                radian, label_offset * ax.get_ylim()[1], label,
                ha='center', va='center', fontsize=12, color='black',
                fontweight='bold'
            )

            # Display min/max values if numeric
            if np.issubdtype(df[label].dtype, np.number):
                min_val = df[label].min()
                max_val = df[label].max()

                # Display min value at the center of the plot
                ax.text(
                    radian, 0, f"{min_val:.2f}",
                    ha='center', va='center', fontsize=10, color='blue', fontweight='bold'
                )

                # Display max value at the end of the radial line
                ax.text(
                    radian, ax.get_ylim()[1], f"{max_val:.2f}",
                    ha='center', va='center', fontsize=10, color='red', fontweight='bold'
                )


        # Save the plot using the fig object
        plot_file_path = "coverage_plot.png"
        fig.savefig(plot_file_path, bbox_inches='tight')
        print(f"Plot saved to {plot_file_path}")

        # Show the plot without opening a new figure
        plt.show()
