"""
This module contains an orchestrator for testing a classifier
"""

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
from development_system.classifier_data import ClassifierData
from development_system.testing_report_generator import TestingReportGenerator


class TestingOrchestrator:
    """
    Class for testing classifiers
    """
    def __init__(self, report_file, generalization_tolerance):
        """
        :param report_file: file for the report
        :param generalization_tolerance: threshold for difference in testing and validation error
        """
        self.report_generator = TestingReportGenerator(report_file, generalization_tolerance)

    def test_classifier(self,
                        classifier: MLPClassifier,
                        classifier_data: ClassifierData,
                        test_data,
                        test_labels):
        """
        Predicts labels from testing set and calculates accuracy error. Generates a report.
        :param classifier:
        :param classifier_data:
        :param test_data:
        :param test_labels:
        :return:
        """
        testing_error = 1 - accuracy_score(test_labels, classifier.predict(test_data))
        self.report_generator.generate_report(classifier_data, testing_error)

        print("Test finished")
