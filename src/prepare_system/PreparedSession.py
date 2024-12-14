import pandas as pd
class PreparedSession():
    def __init__(self, features,UUID):
        self.UUID = UUID
        self.mean_abs_diff_ts = features[0]
        self.mean_abs_diff_am = features[1]
        self.median_long = features[2]
        self.median_lat = features[3]
        self.median_targetIP = features[4]
        self.median_destIP = features[5]