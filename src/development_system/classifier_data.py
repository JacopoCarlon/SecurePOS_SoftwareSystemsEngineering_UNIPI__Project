"""
This module contains a model for classifier statistics
"""


class ClassifierData:
    """
    Class for classifier data
    """
    def __init__(self, classifier_id, layers, neurons, training_error, validation_error):
        """
        :param classifier_id: index of classifier
        :param layers: number of layers
        :param neurons: number of neurons in each layer
        :param training_error: error on testing set
        :param validation_error: error on validation set
        """
        self.classifier_id = classifier_id
        self.layers = layers
        self.neurons = neurons
        self.training_error = training_error
        self.validation_error = validation_error


def from_dict(data: dict) -> ClassifierData:
    trimmed_data = {}
    keys = ["classifier_id", "layers", "neurons", "training_error", "validation_error"]
    for old_key in data:
        if old_key in keys:
            trimmed_data[old_key] = data[old_key]

    for key in keys:
        if key not in trimmed_data:
            print("Missing values")
            return None

    return ClassifierData(**trimmed_data)
