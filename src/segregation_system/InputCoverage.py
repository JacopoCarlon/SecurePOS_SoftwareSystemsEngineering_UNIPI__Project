import json
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from src.db_sqlite3 import DatabaseController

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
        self.uncovered_features = self.outcome["uncovered_features"]


class CheckInputCoverage:
    def __init__(self):
        self.statistics = {}

    def retrieve_statistics(self):
        query = """
        SELECT PS.median_longitude as longitude, PS.median_latitude as latitude, PS.mean_diff_time as time, PS.mean_diff_amount as amount, PS.median_targetIP as targetIP, PS.median_destIP as destIP FROM prepared_sessions PS
        """

        db = DatabaseController(os.path.abspath("database.db"))

        data = db.read_sql(query)
        return data

    def set_stats(self):
        data = self.retrieve_statistics()

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

        degrees = np.linspace(0, 360, num_features, endpoint=False)
        radians = np.radians(degrees)

        marker = 'o'
        colors = ['r', 'g', 'b', 'c', 'm', 'y']

        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        for i in range(num_samples):
            for j in range(num_samples):
                ax.scatter(radians[j], df.iloc[i, j], label=df.columns[j], marker=marker, color=colors[j], s=50, alpha=0.7)

        plt.title("Input Coverage")
        plt.savefig("coverage_plot.png")