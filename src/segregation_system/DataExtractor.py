"""
This module is responsible for extracting data from the database.
"""
import os
from db_sqlite3 import DatabaseController


class DataExtractor:
    """
    This class is responsible for extracting data from the database.
    """
    def __init__(self):
        """
        Constructor for the DataExtractor class.
        - db: DatabaseController object
        """
        self.db = DatabaseController(os.path.abspath("database.db"))

    def extract_grouped_labels(self):
        """
        This method extracts the labels and the number of samples for each label.
        :return: labels: list of tuples with label and number of samples
        """
        lquery = """
        SELECT PS.label as label, COUNT(*) as samples FROM prepared_sessions PS
        GROUP BY PS.label;
        """

        labels = self.db.read_sql(lquery)
        return labels

    def extract_labels(self):
        """
        This method extracts the labels from the database.
        :return: labels: list of labels
        """
        lquery = """
        SELECT PS.label as label FROM prepared_sessions PS
        """

        labels = self.db.read_sql(lquery)
        return labels

    def extract_features(self):
        """
        This method extracts the features from the database.
        :return: data: list of features
        """
        fquery = """
        SELECT PS.median_longitude as longitude, PS.median_latitude as latitude, PS.mean_diff_time as time, PS.mean_diff_amount as amount, PS.median_targetIP as targetIP, PS.median_destIP as destIP FROM prepared_sessions PS
        """

        data = self.db.read_sql(fquery)
        return data

    def extract_all(self):
        """
        This method extracts all the data from the database.
        :return: data: list of all the data
        """
        aquery = """
        SELECT * FROM prepared_sessions;
        """

        data = self.db.read_sql(aquery)
        return data