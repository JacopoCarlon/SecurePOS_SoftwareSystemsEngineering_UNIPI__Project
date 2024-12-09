import json
import pandas as pd
from sklearn.model_selection import train_test_split
from src.segregation_system.DataExtractor import DataExtractor


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
        self.data_extractor = DataExtractor()

    def generate_sets(self):
        input_data = self.data_extractor.extract_all()
        input_labels = self.data_extractor.extract_labels()

        print(f"input_data shape: {len(input_data)}")
        print(f"input_labels shape: {len(input_labels)}")

        percentage = 1 - self.parameters.train_percentage
        x_train, x_tmp, y_train, y_tmp = train_test_split(
            input_data, input_labels, stratify=input_labels, test_size=percentage
        )

        x_validation, x_test, y_validation, y_test = train_test_split(
            x_tmp, y_tmp, stratify=y_tmp, test_size=0.5
        )

        # Combine features and labels for the training set
        training_set = pd.DataFrame(x_train)
        training_set['label'] = y_train

        # Combine features and labels for the validation set
        validation_set = pd.DataFrame(x_validation)
        validation_set['label'] = y_validation

        # Combine features and labels for the test set
        test_set = pd.DataFrame(x_test)
        test_set['label'] = y_test

        return LearningSet(training_set, validation_set, test_set)

    def save_sets(self):
        sets = self.generate_sets()

        sets.training_set.to_json('training_set.json', orient='records')
        sets.validation_set.to_json('validation_set.json', orient='records')
        sets.test_set.to_json('test_set.json', orient='records')

