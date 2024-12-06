"""
This module is responsible for storing and managing prepared sessions
coming from the preparation system.
"""

import json
import pandas as pd
from src.db_sqlite3 import DatabaseController


class PreparedSession:
    """
    Class that holds the field of a prepared session.
    """
    def __init__(self, input_data):
        self.uuid = str(input_data["uuid"])
        self.label = str(input_data["label"])
        self.median_longitude = float(input_data["median_longitude"])
        self.median_latitude = float(input_data["median_latitude"])
        self.mean_diff_time = float(input_data["mean_diff_time"])
        self.mean_diff_amount = float(input_data["mean_diff_amount"])
        self.median_targetIP = str(input_data["median_targetIP"])
        self.median_destIP = str(input_data["median_destIP"])


class PreparedSessionController:
    """
    Class that manages the prepared sessions.
    """
    def __init__(self):
        pass

    def sessions_count(self):
        """
        Count the number of prepared sessions in the database.
        :return: the number of prepared sessions in the database
        """
        db = DatabaseController(
            """
            Path of the database
            """
        )

        query = """
        SELECT COUNT(*) FROM prepared_sessions;
        """

        return db.read_sql(query).iloc[0, 0]

    def store(self, path):
        """
        Store a prepared session in the database.
        :param path: the path of the json file that contain the prepared session to store
        """
        db = DatabaseController(
            """
            Path of the database
            """
        )

        create_table_query = """
        CREATE TABLE IF NOT EXISTS prepared_sessions (
            uuid TEXT PRIMARY KEY,
            label TEXT,
            median_longitude REAL,
            median_latitude REAL,
            mean_diff_time REAL,
            mean_diff_amount REAL,
            median_targetIP TEXT,
            median_destIP TEXT
        );
        """

        db.create_table(create_table_query, [])

        with open(path, "r") as f:
            sessions = json.load(f)

        df = pd.DataFrame(sessions)
        if db.insert(df, "prepared_sessions"):
            print("Data inserted successfully")
            return True
        else:
            print("Data insertion failed")
            return False
