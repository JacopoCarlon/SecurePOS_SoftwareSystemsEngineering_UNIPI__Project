"""
This module contains the orchestrator for classifier training
"""

from sklearn.neural_network import MLPClassifier
from development_system.learning_curve_controller import LearningCurveController


class TrainingOrchestrator:
    """
    Orchestrator for training an MLP classifier
    """
    def __init__(self,  learning_curve_path):
        """
        Initialize training orchestrator
        :param learning_curve_path: path to the file for plotting learning curves
        """
        self.training_params = {}
        self.learning_curve_controller = LearningCurveController(learning_curve_path)

    def set_parameters(self, params: dict) -> None:
        """
        Set training parameters
        :param params: dictionary of 'parameter-name: value' couples
        :return: None
        """
        self.training_params.update(params)

    def generate_learning_curve(self, training_data, training_labels) -> None:
        """
        Generate a new learning curve
        :param training_data: training set features
        :param training_labels: training set labels
        :return: None
        """
        tmp_classifier = MLPClassifier(random_state=42,
                                       **self.training_params)
        tmp_classifier.fit(training_data, training_labels)
        self.learning_curve_controller.update_learning_curve(tmp_classifier.loss_curve_)

    def train_classifier(self, training_data, training_labels) -> MLPClassifier:
        """
        Train an MLP classifier
        :param training_data: training set features
        :param training_labels: training set labels
        :return: fitted MLPClassifier
        """
        classifier = MLPClassifier(**self.training_params)
        classifier.fit(training_data, training_labels)
        return classifier
