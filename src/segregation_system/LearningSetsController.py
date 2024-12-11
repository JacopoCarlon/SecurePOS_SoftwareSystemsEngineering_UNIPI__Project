import json
import pandas as pd
import requests
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

        # Replace label strings with integers
        label_mapping = {
            "label1": 0,
            "label2": 1,
            "label3": 2
        }
        input_labels = input_labels.replace(label_mapping)

        x_train, x_tmp, y_train, y_tmp = train_test_split(
            input_data, input_labels, stratify=input_labels, test_size=0.3
        )

        print(f"x_train shape: {len(x_train)}")
        print(f"x_tmp shape: {len(x_tmp)}")
        print(f"y_train shape: {len(y_train)}")
        print(f"y_tmp shape: {len(y_tmp)}")

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
        sets = self.generate_sets()

        # Create a dictionary to store all sets
        all_sets = {
            "training_set": sets.training_set.to_dict(orient='records'),
            "validation_set": sets.validation_set.to_dict(orient='records'),
            "test_set": sets.test_set.to_dict(orient='records')
        }

        # Save the dictionary as a single JSON file
        with open('all_sets.json', 'w') as f:
            json.dump(all_sets, f, indent='\t')

    def send_learning_sets(self, filepath):
        url = 'http://localhost:5000/file_reception'
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        print("DEBUG> Response from server: ", response.status_code)