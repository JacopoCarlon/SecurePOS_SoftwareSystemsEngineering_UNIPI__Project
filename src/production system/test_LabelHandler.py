import unittest
from unittest.mock import patch, MagicMock
from LabelHandler import LabelHandler

class TestLabelHandler(unittest.TestCase):
    def setUp(self):
        self.label_data = {'uuid': '1234', 'label': 'test_label'}
        self.label_handler = LabelHandler(self.label_data)

    @patch('jsonIO.jsonIO')
    def test_send_label_evaluation(self, mock_jsonIO):
        mock_instance = mock_jsonIO.return_value
        self.label_handler.send_lable(phase='evaluation')
        mock_instance.send_message.assert_called_once_with({'uuid': '1234', 'label': 'test_label'})

    @patch('jsonIO.jsonIO')
    def test_send_label_production(self, mock_jsonIO):
        mock_instance = mock_jsonIO.return_value
        self.label_handler.send_lable(phase='production')
        mock_instance.send_message.assert_called_once_with({'uuid': '1234', 'label': 'test_label'})

if __name__ == '__main__':
    unittest.main()