"""
API class which handle file reception and sending.
To be used, the API has to be added as a resource to Flask application
"""

import os
from flask import request, abort, send_file
from flask_restful import Resource

from utility import data_folder


class FileReceptionAPI(Resource):
    """
    This API allows other nodes to send files to the REST server.
    """
    def __init__(self, filename):
        """
        Initialize API
        :param filepath: path where to save received file
        """
        self.filepath = os.path.join(data_folder, filename)

    def post(self):
        """
        Handle a POST request.
        Other nodes should send a POST request when they want to send a file to this endpoint.
        The file must be inserted in the ``files['file']`` field of the request.
        :return: status code 201 on success, 400 if the file does not exist
        """
        # Check if request contains a file
        if 'file' not in request.files:
            return abort(400)

        # Save file
        file = request.files['file']
        file.save(self.filepath)

        return 'File received', 201

    def get(self):
        """
        Handle a GET request.
        Other nodes should send a GET request when they want to get a file from this endpoint.
        :return: the file requested
        """
        if not os.path.exists(self.filepath):
            return abort(404)

        return send_file(self.filepath, as_attachment=True)