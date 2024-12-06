from unittest import TestCase
from unittest.mock import MagicMock
from flask import Flask
from jsonIO import jsonIO

class TestJsonIO(TestCase):

    def setUp(self):
        # Set up a Flask application instance
        self.app = Flask(__name__)
        self.filepath = "/tmp/testfile.txt"
        self.json_io = jsonIO(self.filepath)

    def test_post_success(self):
        # Simulate a test request context
        with self.app.test_request_context(method='POST', data={'file': (b'file content', 'testfile.txt')}):
            # Mock request.files
            from flask import request
            mock_file = MagicMock()
            mock_file.read.return_value = b"file content"
            request.files = {'file': mock_file}

            # Call the post method
            response, status_code = self.json_io.post()

            # Assertions
            self.assertEqual(status_code, 201)
            self.assertEqual(response, b"file content")
