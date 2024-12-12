"""
This module is responsible for generating the learning sets for the development system.
"""

import json
import pandas as pd
import requests
from sklearn.model_selection import train_test_split
from src.segregation_system.DataExtractor import DataExtractor

parameters_path = '../../data/segregation_system/config/learning_sets_parameters.json'
file_path = '../../data/segregation_system/sets/all_sets.json'

class LearningSetsParameters:
    """
    This class is responsible for loading the parameters for the learning sets generation.
    """
    def __init__(self):
        """
        Constructor for the LearningSetsParameters class.
        """

        """
        Load the parameters from the JSON file.
        - trainPercentage: percentage of the training set
        - testPercentage: percentage of the test set
        - validationPercentage: percentage of the validation set
        """
        try:
            with open(parameters_path) as f:
                config = json.load(f)
                self.train_percentage = int(config['trainPercentage'])
                self.test_percentage = int(config['testPercentage'])
                self.validation_percentage = int(config['validationPercentage'])
        except FileNotFoundError:
            print('ERROR> Parameters file not found')
        except json.JSONDecodeError:
            print('ERROR> Error decoding JSON file')


class LearningSet:
    """
    This class is responsible for storing the learning sets.
    """
    def __init__(self, training_set, validation_set, test_set):
        """
        Constructor for the LearningSet class.
        :param training_set: data structure that stores the training set
        :param validation_set: data structure that stores the validation set
        :param test_set: data structure that stores the test set
        """
        self.training_set = training_set
        self.validation_set = validation_set
        self.test_set = test_set


class LearningSetsController:
    """
    This class is responsible for generating the learning sets for the development system.
    """
    def __init__(self):
        """
        Constructor for the LearningSetsController class.
        """

        """
        Initialize the parameters and the data extractor.
        - parameters: object that stores the parameters for the learning sets generation
        - data_extractor: object that extracts the data from the database
        """
        self.parameters = LearningSetsParameters()
        self.data_extractor = DataExtractor()

    def generate_sets(self):
        """
        This method is responsible for generating the learning sets.
        :return: learning sets
        """

        """
        Extract the data and the labels from the database.
        """
        input_data = self.data_extractor.extract_all()
        input_labels = self.data_extractor.extract_labels()

        """
        Convert the labels to numerical values.
        """
        label_mapping = {
            "normal": 0,
            "moderate": 1,
            "high": 2
        }
        input_labels = input_labels.replace(label_mapping)

        """
        Generate the training set and the temporary set that will be split into the validation and test sets.
        """
        x_train, x_tmp, y_train, y_tmp = train_test_split(
            input_data, input_labels, stratify=input_labels, test_size=0.3
        )

        """
        Split the temporary set into the validation and test sets.
        """
        x_validation = x_tmp[:len(x_tmp) // 2]
        x_test = x_tmp[len(x_tmp) // 2:]
        y_validation = y_tmp[:len(y_tmp) // 2]
        y_test = y_tmp[len(y_tmp) // 2:]

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
        """
        This method is responsible for saving the learning sets to a JSON file.
        """
        sets = self.generate_sets()

        # Create a dictionary to store all sets
        all_sets = {
            "training_set": sets.training_set.to_dict(orient='records'),
            "validation_set": sets.validation_set.to_dict(orient='records'),
            "test_set": sets.test_set.to_dict(orient='records')
        }

        # Save the dictionary as a single JSON file
        with open(file_path, 'w') as f:
            json.dump(all_sets, f, indent='\t')

    def send_learning_sets(self, filepath, endpoint):
        """
        This method is responsible for sending the learning sets to the development system.
        :param filepath: path to the JSON file that stores the learning sets
        :param endpoint: URL of the development system
        """
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(endpoint, files=files)
        print("Response from server: ", response.status_code)
