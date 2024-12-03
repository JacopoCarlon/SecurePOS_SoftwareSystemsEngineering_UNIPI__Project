import jsonIO
import joblib

class classifierModelController:
    def __init__(self):
        self.load_classifier()
        pass

    def load_classifier(self):
        hyperparameters = jsonIO.jsonIO().receive_message()


        self.num_inputs = hyperparameters['num_inputs']
        self.num_layers = hyperparameters['num_layers']
        self.num_neurons = hyperparameters['num_neurons']
        self.training_error = hyperparameters['training_error']
        
        #save the model file which is a joblib file in hyperparameters['model_file]
        self.model = joblib.load(hyperparameters['model_file'])

        #TODO: load the actual model
        pass

    def get_classifier_model(self):
        return self.model
        pass

    def classify(self, data):
        return self.model.predict(data)
        pass

    def predict(self, data):
        #TODO: acctual call to the model
        return 