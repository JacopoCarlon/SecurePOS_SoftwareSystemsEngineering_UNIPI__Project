import json
import requests
from flask import request, abort
from flask_restful import Resource

class jsonIO(Resource):

        def __init__(self, filepath):
            self.filepath = filepath
            pass

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

            return file.read(), 201