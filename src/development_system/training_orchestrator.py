class TrainingOrchestrator:
    def __init__(self):
        self.training_parameters = {
            "num_features": 5
        }

    def set_parameters(self, params: dict) -> bool:
        """
        Set training parameters
        :param params: dictionary of inputs
        :return: True if passed parameters were configured correctly, False otherwise
        """

        if "num_iterations" in params:
            if params["num_iterations"] < 2:
                print("ERROR: iterations should be at least 2")
                return False
            self.training_parameters["num_iterations"] = params["num_iterations"]

        if "num_layers" in params:
            if params["num_layers"] < 1:
                print("ERROR: layers should be at least 1")
                return False
            self.training_parameters["num_layers"] = params["num_layers"]

        if "num_neurons" in params:
            if params["num_neurons"] < 1:
                print("ERROR: neurons in each layer should be at least 1")
                return False
            self.training_parameters["num_neurons"] = params["num_neurons"]

        return True

    
