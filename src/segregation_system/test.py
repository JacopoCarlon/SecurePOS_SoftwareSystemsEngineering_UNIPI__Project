import json

import requests
import os
from utility import data_folder

def test_send_prepared_session():
    """
    Test the sending of a json file with the structure of a prepared session.
    """
    url = "http://192.168.159.110:5000/upload"
    json_filename = os.path.join(data_folder, 'segregation_system', 'prepared_sessions.json')
    
    with open(json_filename, 'r') as file:
        json_data = json.load(file)
    
    response = requests.post(url, json=json_data)
    print(response.text)
    assert response.status_code == 201

if __name__ == "__main__":
    test_send_prepared_session()
    print("Test passed")