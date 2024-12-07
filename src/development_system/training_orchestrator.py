from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import learning_curve
from development_system.learning_curve_controller import LearningCurveController


class TrainingOrchestrator:
    def __init__(self):
        self.num_iterations = 2
        self.num_layers = 1
        self.num_neurons = 1
        self.hidden_layer_sizes = (1,)
        self.learning_curve_controller = LearningCurveController()

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
            self.num_iterations = params["num_iterations"]

        if "num_layers" in params:
            if params["num_layers"] < 1:
                print("ERROR: layers should be at least 1")
                return False
            self.num_layers = params["num_layers"]

        if "num_neurons" in params:
            if params["num_neurons"] < 1:
                print("ERROR: neurons in each layer should be at least 1")
                return False
            self.num_neurons = params["num_neurons"]

        self.hidden_layer_sizes = []
        for i in range(self.num_layers):
            self.hidden_layer_sizes.append(self.num_neurons)
        self.hidden_layer_sizes = tuple(self.hidden_layer_sizes)

        return True

    def generate_learning_curve(self, x_train, y_train):
        """
        Generate a new learning curve
        :param x_train: training set features
        :param y_train: training set labels
        :return: None
        """
        tmp_classifier = MLPClassifier(hidden_layer_sizes=self.hidden_layer_sizes,
                                       max_iter=self.num_iterations,
                                       random_state=42)
        tmp_classifier.fit(x_train, y_train)
        self.learning_curve_controller.update_learning_curve(tmp_classifier.loss_curve_)

