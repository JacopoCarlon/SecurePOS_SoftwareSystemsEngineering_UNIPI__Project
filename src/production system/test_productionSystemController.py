import unittest
from unittest.mock import MagicMock, patch
from productionSystemController import ProductionSystemController

class TestProductionSystemController(unittest.TestCase):

    @patch('productionSystemController.ClassifierModelController.classifierModelController')
    def test_handle_classifier_model_deployment(self, MockClassifierModelController):
        controller = ProductionSystemController()
        controller.handle_classifier_model_deployment()
        MockClassifierModelController.assert_called_once()

    @patch('productionSystemController.PrepareSessionHandler.PrepareSessionHandler')
    def test_handle_prepared_session_reception(self, MockPrepareSessionHandler):
        mock_session_handler = MockPrepareSessionHandler.return_value
        mock_session_handler.new_session.return_value = 'mock_session'
        
        controller = ProductionSystemController()
        controller.handle_prepared_session_reception()
        
        MockPrepareSessionHandler.assert_called_once()
        mock_session_handler.new_session.assert_called_once()
        self.assertEqual(controller.session, 'mock_session')

    @patch('productionSystemController.LabelHandler.LabelHandler')
    @patch('productionSystemController.ClassifierModelController.classifierModelController')
    @patch('productionSystemController.PrepareSessionHandler.PrepareSessionHandler')
    def test_run_classification_task(self, MockPrepareSessionHandler, MockClassifierModelController, MockLabelHandler):
        mock_session_handler = MockPrepareSessionHandler.return_value
        mock_session_handler.new_session.return_value.session_request.return_value = 'mock_request'
        
        mock_classifier = MockClassifierModelController.return_value
        mock_classifier.classify.return_value = 'mock_label'
        
        controller = ProductionSystemController()
        controller.handle_classifier_model_deployment()
        controller.handle_prepared_session_reception()
        controller.run_classsification_task()
        
        mock_classifier.classify.assert_called_once_with('mock_request')
        MockLabelHandler.assert_called_once_with('mock_label')

    @patch('productionSystemController.LabelHandler.LabelHandler')
    def test_send_label(self, MockLabelHandler):
        mock_label_handler = MockLabelHandler.return_value
        
        controller = ProductionSystemController()
        controller.label = mock_label_handler
        controller.send_label()
        
        mock_label_handler.send_label.assert_called_once()

    @patch('productionSystemController.LabelHandler.LabelHandler')
    def test_send_label_evaluation(self, MockLabelHandler):
        mock_label_handler = MockLabelHandler.return_value
        
        controller = ProductionSystemController()
        controller.label = mock_label_handler
        controller.send_label_evaluation()
        
        mock_label_handler.send_label.assert_called_once_with('evaluation')

    @patch('productionSystemController.handle_classifier_model_deployment')
    @patch('productionSystemController.handle_prepared_session_reception')
    @patch('productionSystemController.run_classification_task')
    @patch('productionSystemController.send_label')
    def test_run(self, mock_send_label, mock_run_classsification_task, mock_handle_prepared_session_reception, mock_handle_classifier_model_deployment):
        controller = ProductionSystemController()
        
        # To stop the infinite loop after one iteration
        mock_handle_prepared_session_reception.side_effect = RuntimeError("Stop loop")
        
        with self.assertRaises(RuntimeError):
            controller.run()
        
        mock_handle_classifier_model_deployment.assert_called_once()
        mock_handle_prepared_session_reception.assert_called_once()
        mock_run_classsification_task.assert_called_once()
        mock_send_label.assert_called_once()

if __name__ == '__main__':
    unittest.main()