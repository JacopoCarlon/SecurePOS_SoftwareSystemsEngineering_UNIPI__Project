import json
import pandas as pd
from db_sqlite3 import DatabaseController

class LearningSetsParameters:
    def __init__(self):
        try:
            with open('learningSetsParameters.json') as f:
                config = json.load(f)
                self.train_percentage = int(config['trainPercentage'])
                self.test_percentage = int(config['testPercentage'])
                self.validation_percentage = int(config['validationPercentage'])
        except FileNotFoundError:
            print('Parameters file not found')
        except json.JSONDecodeError:
            print('Error decoding JSON file')


class LearningSet:
    def __init__(self, training_set, validation_set, test_set):
        self.training_set = training_set
        self.validation_set = validation_set
        self.test_set = test_set


class LearningSetsController:
    def __init__(self):
        self.parameters = LearningSetsParameters()
        self.db = DatabaseController('database.db')

    def generate_sets(self):
        query = """
        SELECT * FROM prepared_sessions;
        """

        data = self.db.read_sql(query)

        df = pd.DataFrame(
            data,
            columns=['uuid', 'label', 'median_longitude', 'median_latitude', 'mean_diff_time', 'mean_diff_amount', 'median_targetIP', 'median_destIP']
        )

        data_len = len(df)
        train_len = int(data_len * self.parameters.train_percentage)
        training_set = df.iloc[:train_len]

        print('Training set:')
        print(training_set)

        validation_len = int(data_len * self.parameters.validation_percentage)
        validation_set = df.iloc[train_len:train_len + validation_len]

        print('Validation set:')
        print(validation_set)

        test_set = df.iloc[train_len + validation_len:]

        print('Test set:')
        print(test_set)

        return LearningSet(training_set, validation_set, test_set)

    def save_sets(self):
        sets = self.generate_sets()

        sets.training_set.to_json('training_set.json', orient='records')
        sets.validation_set.to_json('validation_set.json', orient='records')
        sets.test_set.to_json('test_set.json', orient='records')

