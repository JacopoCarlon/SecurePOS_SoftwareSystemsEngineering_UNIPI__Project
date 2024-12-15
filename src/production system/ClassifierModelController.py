import os
import time
import json
import joblib
from sklearn.neural_network import MLPClassifier

class ClassifierModelController:
    """
    Controller class for managing and using a classifier model.

    Methods:
    --------
    __init__():
        Initializes the ClassifierModelController instance, loads hyperparameters, and loads the classifier model.
    get_hyperparameters():
        Retrieves hyperparameters from a JSON file.
    load_classifier():
        Loads the classifier model using the hyperparameters.
    get_classifier_model():
        Returns the loaded classifier model.
    classify(data):
        Classifies the given data using the loaded model.
    predict(data):
        Placeholder method for predicting data using the model.
    """
    def __init__(self):
        """
        Initializes the ClassifierModelController.

        This includes creating an instance of the JSON I/O handler and loading the classifier model with its hyperparameters.
        """
        print("Initializing ClassifierModelController")
        self.load_classifier()
        

    def get_hyperparameters(self):
        """
        Retrieves hyperparameters for the classifier model.

        The hyperparameters are fetched using the JSON I/O handler from a predefined source.
        
        Returns:
        --------
        dict
            A dictionary containing hyperparameters like 'num_inputs', 'num_layers', 'num_neurons', 
            'training_error', and 'model_file'.
        """
        # Check if the file exists
        while not os.path.exists(os.path.join('src', 'production system', 'model', 'hyperparameters.json')):
            print("File not found, waiting...")
            time.sleep(2)
        print("File found")
        with open(os.path.join('src', 'production system', 'model', 'hyperparameters.json'), 'r') as file:
            hyperparameters = json.load(file)
        return hyperparameters

    def load_classifier(self):
        """
        Loads the classifier model using hyperparameters.

        Extracts necessary details like the number of inputs, layers, neurons, and training error from the hyperparameters.
        Uses the 'model_file' path from hyperparameters to load the model with joblib.
        """
        hyperparameters = self.get_hyperparameters()
        print("Hyperparameters:", hyperparameters)
        self.hyperparameters = hyperparameters
        # load the model from a file
        self.model = joblib.load(os.path.join('src', 'production system', 'model', 'classifier_model.joblib'))
        print("Model loaded:", self.model)
        


    def classify(self, data):
        """
        Classifies the given data using the loaded model.

        Parameters:
        -----------
        data : array-like
            The input data to classify.

        Returns:
        --------
        array
            The classification results.
        """
        if not hasattr(self, 'model'):
            raise Exception("Model not loaded")
        return self.model.predict(data)

    def get_classifier_model(self):
        """
        Returns the loaded classifier model.

        Returns:
        --------
        MLPClassifier
            The loaded classifier model.
        """
        if not hasattr(self, 'model'):
            raise Exception("Model not loaded")
        return self.model