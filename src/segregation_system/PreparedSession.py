"""
This module is responsible for storing and managing prepared sessions
coming from the preparation system.
"""

import json
import pandas as pd
import os
from db_sqlite3 import DatabaseController
from utility.json_validation import validate_json_data_file
from utility import data_folder, project_root

DATABASE_PATH = os.path.join(project_root, 'src', 'segregation_system', 'segregationDB.db')
SCHEMA_PATH = os.path.join(data_folder, 'segregation_system', 'schemas', 'prepared_session_schema.json')

class PreparedSession:
    """
    Class that holds the field of a prepared sessions
    """
    def __init__(self, input_data):
        """
        Constructor of the PreparedSession class.
        """
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
        """
        Constructor of the PreparedSessionController class.
        """
        pass

    def sessions_count(self):
        """
        Count the number of prepared sessions in the database.
        :return: the number of prepared sessions in the database
        """
        db = DatabaseController(DATABASE_PATH)

        query = """
        SELECT COUNT(*) FROM prepared_sessions WHERE to_process = 1;
        """

        return db.read_sql(query).iloc[0, 0]

    def store(self, path, to_process):
        """
        Store a prepared session in the database.
        :param path: the path of the json file that contain the prepared session to store
        """

        db = DatabaseController(DATABASE_PATH)

        with open(path, "r") as f:
            sessions = json.load(f)

        if not validate_json_data_file(sessions, SCHEMA_PATH):
            return False

        df = pd.DataFrame([sessions]).rename(columns={
            "UUID": "uuid",
            "mean_abs_diff_ts": "mean_diff_time",
            "mean_abs_diff_am": "mean_diff_amount",
            "median_long": "median_longitude",
            "median_lat": "median_latitude",
            "median_targetIP": "median_targetIP",
            "median_destIP": "median_destIP"
        })

        df["to_process"] = to_process

        return db.insert_dataframe(df, "prepared_sessions")
