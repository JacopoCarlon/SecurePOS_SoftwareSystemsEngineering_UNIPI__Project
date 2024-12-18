import os
import time
import json
import joblib
import pandas as pd

# Aggiungi il percorso del modulo utility
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utility

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
        self.model = None
        while self.model is None:
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
        while not os.path.exists('model/hyperparameters.json'):
            time.sleep(1)
        with open('model/hyperparameters.json', 'r') as file:
            hyperparameters = json.load(file)
        return hyperparameters

    def load_classifier(self):
        """
        Loads the classifier model using hyperparameters.

        Extracts necessary details like the number of inputs, layers, neurons, and training error from the hyperparameters.
        Uses the 'model_file' path from hyperparameters to load the model with joblib.
        """
        model_file = os.path.join('src', 'production_system', 'model', 'classifier_model.joblib')
        
        while not os.path.exists(model_file):
            time.sleep(1)

        # load the classifier model
        try:
            self.model = joblib.load(model_file)
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
            return False
        return True
        

    def classify(self, data):
        """
        Classifies the given data using the loaded model.

        Parameters:
        -----------
        data : dict
            The input data to classify.

        Returns:
        --------
        array
            The classification results.
        """
        if not hasattr(self, 'model'):
            raise Exception("Model not loaded")
        
        start_time = time.time()
        # Estrai le caratteristiche rilevanti dal dizionario
        features = {
            'median_longitude': data['median_coordinates'][1],
            'median_latitude': data['median_coordinates'][0],
            'mean_diff_time': data['mean_diff_time'],
            'mean_diff_amount': data['mean_diff_amount'],
            'median_targetIP': utility.ip_to_float(data['mean_target_ip']),  # Converti IP a float
            'median_destIP': utility.ip_to_float(data['mean_dest_ip'])  # Converti IP a float
        }
        # Converti le caratteristiche in un DataFrame di pandas
        features_df = pd.DataFrame([features])
        # Predici con il modello
        y_pred = self.model.predict(features_df)  # Usa il modello caricato
        end_time = time.time()
        print("Classification took ", end_time - start_time, " seconds")
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