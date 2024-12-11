"""
This module contains a class for validation orchestration
"""

import json
import os
import itertools
import joblib
from sklearn.metrics import accuracy_score
from development_system.validation_report_generator import ValidationReportGenerator
from development_system.training_orchestrator import TrainingOrchestrator
from development_system.classifier_data import ClassifierData


class ValidationOrchestrator:
    """
    Class for validating classifiers
    """
    def __init__(self,
                 validation_config_file: str,
                 classifier_folder: str,
                 report_path: str,
                 training_orchestrator: TrainingOrchestrator):
        """
        Initialize validator
        :param validation_config_file: path to file that contains validation parameters
        :param classifier_folder: folder where fitted classifiers are stored
        :param report_path: path to file in which the report will be written
        :param training_orchestrator: orchestrator of training
        """
        self.classifier_folder = classifier_folder
        self.training_orchestrator = training_orchestrator

        with open(validation_config_file, "r", encoding="UTF-8") as file:
            conf_json = json.load(file)

            self.min_layers = conf_json['min_layers']
            self.step_layers = conf_json['step_layers']
            self.max_layers = conf_json['max_layers']

            self.min_neurons = conf_json['min_neurons']
            self.step_neurons = conf_json['step_neurons']
            self.max_neurons = conf_json['max_neurons']

            overfitting_tolerance = conf_json["overfitting_tolerance"]

        self.report_generator = ValidationReportGenerator(report_path, overfitting_tolerance)

    def retrieve_average_parameters(self) -> dict:
        """
        Calculates average values of hyperparameters
        :return: a dictionary of said values
        """
        avg_layers = (self.min_layers + self.max_layers) / 2
        avg_neurons = (self.min_neurons + self.max_neurons) / 2
        hidden_layer_sizes = tuple(itertools.repeat(avg_neurons, avg_layers))
        return {
            "hidden_layer_sizes": hidden_layer_sizes
        }

    def save_model_to_file(self, classifier, index) -> None:
        """
        Saves fitted classifier
        :param classifier: fitted model
        :param index: index of the classifier
        :return: None
        """
        filepath = os.path.join(self.classifier_folder, f'model_{index}.sav')
        joblib.dump(classifier, filepath)

    def grid_search(self, train_data, train_labels, val_data, val_labels) -> None:
        """
        Starts a grid search using validation parameters.
        :param train_data: features for classifier training
        :param train_labels: labels for classifier training
        :param val_data: features for classifier validation
        :param val_labels: labels for classifier validation
        :return: None
        """
        index = 1

        for layers in range(self.min_layers, self.max_layers+1, self.step_layers):
            for neurons in range(self.min_neurons, self.max_neurons+1, self.step_neurons):
                hidden_layer_sizes = tuple(itertools.repeat(neurons, layers))

                self.training_orchestrator.set_parameters({
                    "hidden_layer_sizes": hidden_layer_sizes
                })

                classifier = self.training_orchestrator.train_classifier(train_data, train_labels)
                training_error = 1 - accuracy_score(train_labels, classifier.predict(train_data))
                validation_error = 1 - accuracy_score(val_labels, classifier.predict(val_data))

                cd = ClassifierData(index, layers, neurons, training_error, validation_error)
                self.report_generator.add_row(cd)

                self.save_model_to_file(classifier, index)
                print(f'Trained classifier {index}\n')
                index += 1

        self.report_generator.generate_report()
        print("End of Grid Search")