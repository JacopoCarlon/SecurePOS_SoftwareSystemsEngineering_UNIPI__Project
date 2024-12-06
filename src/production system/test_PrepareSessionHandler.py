import unittest
from unittest.mock import MagicMock
from PrepareSessionHandler import PrepareSessionHandler

class TestPrepareSessionHandler(unittest.TestCase):

    def setUp(self):
        self.filepath = 'test_filepath'
        self.handler = PrepareSessionHandler(self.filepath)
        self.handler.jsonIO = MagicMock()

    def test_new_session_success(self):
        # Mock the response from jsonIO.post
        message = {
            'uuid': '1234',
            'label': 'test_label',
            'median_coordinates': [1.0, 2.0],
            'mean_diff_time': 0.5,
            'mean_diff_amount': 100.0,
            'mean_target_ip': '192.168.1.1',
            'mean_dest_ip': '192.168.1.2'
        }
        self.handler.jsonIO.post.return_value = (message, 201)

        # Call the method
        self.handler.new_session()

        # Check if the attributes are set correctly
        self.assertEqual(self.handler.uuid, '1234')
        self.assertEqual(self.handler.label, 'test_label')
        self.assertEqual(self.handler.median_coordinates, [1.0, 2.0])
        self.assertEqual(self.handler.mean_diff_time, 0.5)
        self.assertEqual(self.handler.mean_diff_amount, 100.0)
        self.assertEqual(self.handler.mean_target_ip, '192.168.1.1')
        self.assertEqual(self.handler.mean_dest_ip, '192.168.1.2')

    def test_new_session_failure(self):
        # Mock the response from jsonIO.post
        self.handler.jsonIO.post.return_value = ({}, 400)

        # Call the method
        self.handler.new_session()

        # Check if the attributes are not set
        self.assertFalse(hasattr(self.handler, 'uuid'))
        self.assertFalse(hasattr(self.handler, 'label'))
        self.assertFalse(hasattr(self.handler, 'median_coordinates'))
        self.assertFalse(hasattr(self.handler, 'mean_diff_time'))
        self.assertFalse(hasattr(self.handler, 'mean_diff_amount'))
        self.assertFalse(hasattr(self.handler, 'mean_target_ip'))
        self.assertFalse(hasattr(self.handler, 'mean_dest_ip'))

    def test_session_request(self):
        # Set the attributes
        self.handler.uuid = '1234'
        self.handler.label = 'test_label'
        self.handler.median_coordinates = [1.0, 2.0]
        self.handler.mean_diff_time = 0.5
        self.handler.mean_diff_amount = 100.0
        self.handler.mean_target_ip = '192.168.1.1'
        self.handler.mean_dest_ip = '192.168.1.2'

        # Call the method
        data = self.handler.session_request()

        # Check if the data is correct
        expected_data = {
            'uuid': '1234',
            'label': 'test_label',
            'median_coordinates': [1.0, 2.0],
            'mean_diff_time': 0.5,
            'mean_diff_amount': 100.0,
            'mean_target_ip': '192.168.1.1',
            'mean_dest_ip': '192.168.1.2'
        }
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()