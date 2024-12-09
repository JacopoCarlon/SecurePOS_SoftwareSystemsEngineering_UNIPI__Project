import os
from db_sqlite3 import DatabaseController


class DataExtractor:
    def __init__(self):
        self.db = DatabaseController(os.path.abspath("database.db"))

    def extract_grouped_labels(self):
        lquery = """
        SELECT PS.label as label, COUNT(*) as samples FROM prepared_sessions PS
        GROUP BY PS.label;
        """

        labels = self.db.read_sql(lquery)
        print("DEBUG> Retrieved labels: ", labels)
        return labels

    def extract_labels(self):
        lquery = """
        SELECT PS.label as label FROM prepared_sessions PS
        """

        labels = self.db.read_sql(lquery)
        return labels

    def extract_features(self):
        fquery = """
        SELECT PS.median_longitude as longitude, PS.median_latitude as latitude, PS.mean_diff_time as time, PS.mean_diff_amount as amount, PS.median_targetIP as targetIP, PS.median_destIP as destIP FROM prepared_sessions PS
        """

        data = self.db.read_sql(fquery)
        return data

    def extract_all(self):
        aquery = """
        SELECT * FROM prepared_sessions;
        """

        data = self.db.read_sql(aquery)
        return data