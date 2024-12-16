import os
import time
import json
import joblib
from sklearn.neural_network import MLPClassifier

import numpy as np
import json

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
        print("Classifying data:", data)
        if not hasattr(self, 'model'):
            raise Exception("Model not loaded")
        data = {
            "X_fake": [2.15, -3.46, 5.28, -1.83, 0.47, -7.22]
        }

        # Converti l'array in NumPy
        X_fake = np.array(data["X_fake"])

        # Reshape per creare un array 2D (1 campione con 6 feature)
        X_input = X_fake.reshape(1, -1)

        # Verifica la forma
        print("Forma di X_input:", X_input.shape)  # Dovrebbe essere (1, 6)

        # Predici con il modello
        y_pred = self.model.predict(X_input)  # Usa il modello caricato
        print("Predizione:", y_pred)
        return y_pred



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