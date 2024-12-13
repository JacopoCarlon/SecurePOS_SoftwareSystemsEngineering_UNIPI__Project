"""
File to test the sending of a json file with the structure of a prepared session.
"""
import json
import requests

def test_send_prepared_session():
    """
    Test the sending of a json file with the structure of a prepared session.
    """
    url = "http://192.168.159.110:5000/"
    json_filename = "prepared_sessions.json"
    response = requests.post(url, json=json_filename)
    assert response.status_code == 201

if __name__ == "__main__":

    test_send_prepared_session()
    print("Test passed")
