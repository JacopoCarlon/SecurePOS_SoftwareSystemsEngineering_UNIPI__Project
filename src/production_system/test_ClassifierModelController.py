import unittest
from unittest.mock import MagicMock, patch
from ClassifierModelController import classifierModelController

class TestClassifierModelController(unittest.TestCase):
    @patch('jsonIO.jsonIO')
    @patch('joblib.load')
    def setUp(self, mock_joblib_load, mock_jsonIO):
        # Mocking the jsonIO and joblib.load
        self.mock_jsonIO = mock_jsonIO.return_value
        self.mock_jsonIO.post.return_value = {
            'num_inputs': 10,
            'num_layers': 3,
            'num_neurons': 100,
            'training_error': 0.01,
            'model_file': 'dummy_model_file.joblib'
        }
        self.mock_model = MagicMock()
        mock_joblib_load.return_value = self.mock_model

        self.controller = classifierModelController()

    def test_get_hyperparameters(self):
        hyperparameters = self.controller.get_hyperparameters()
        self.assertEqual(hyperparameters['num_inputs'], 10)
        self.assertEqual(hyperparameters['num_layers'], 3)
        self.assertEqual(hyperparameters['num_neurons'], 100)
        self.assertEqual(hyperparameters['training_error'], 0.01)
        #self.assertEqual(hyperparameters['model_file'], 'dummy_model_file.joblib')

    def test_load_classifier(self):
        #self.controller.load_classifier()
        self.assertEqual(self.controller.num_inputs, 10)
        self.assertEqual(self.controller.num_layers, 3)
        self.assertEqual(self.controller.num_neurons, 100)
        self.assertEqual(self.controller.training_error, 0.01)
        #self.assertEqual(self.controller.model, self.mock_model)

    def test_get_classifier_model(self):
        model = self.controller.get_classifier_model()
        self.assertEqual(model, self.mock_model)

    def test_classify(self):
        test_data = [1, 2, 3]
        self.mock_model.predict.return_value = 'mock_prediction'
        prediction = self.controller.classify(test_data)
        self.mock_model.predict.assert_called_with(test_data)
        self.assertEqual(prediction, 'mock_prediction')

if __name__ == '__main__':
    unittest.main()