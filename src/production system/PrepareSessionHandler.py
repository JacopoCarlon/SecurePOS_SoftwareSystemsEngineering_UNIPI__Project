import json  # Standard library for working with JSON data
import json_io  # Custom module for JSON input/output operations

class PrepareSessionHandler:
    """
    A handler class for preparing and managing session data.

    Attributes:
        jsonIO (jsonIO.jsonIO): An instance of the jsonIO class for handling JSON input/output operations.
        uuid (str): The unique identifier for the session.
        label (str): The label associated with the session.
        median_coordinates (list): The median coordinates for the session.
        mean_diff_time (float): The mean difference in time for the session.
        mean_diff_amount (float): The mean difference in amount for the session.
        mean_target_ip (str): The mean target IP address for the session.
        mean_dest_ip (str): The mean destination IP address for the session.

    Methods:
        __init__(filepath):
            Initializes the PrepareSessionHandler with the given filepath for JSON I/O operations.

        session_request():
            Creates and returns a JSON object with the session data.

        new_session():
            Retrieves a new session message from the jsonIO, parses it, and updates the session attributes.
    """

    # Constructor for initializing the handler with a file path for JSON I/O
    def __init__(self, filepath):
        # Initialize jsonIO with the specified file path
        self.jsonIO = json_io.jsonIO(filepath)

    def session_request(self):
        """
        Creates and returns a JSON object containing session data.
        This JSON will be based on the class attributes populated from the last session.
        """
        data = {
            # Unique identifier for the session
            'uuid': self.uuid,
            
            # Associated label for the session
            'label': self.label,
            
            # Median coordinates, formatted as a list of two elements
            'median_coordinates': [self.median_coordinates[0], self.median_coordinates[1]],
            
            # Mean time difference between events in the session
            'mean_diff_time': self.mean_diff_time,
            
            # Mean amount difference between events in the session
            'mean_diff_amount': self.mean_diff_amount,
            
            # The mean target IP address observed in the session
            'mean_target_ip': self.mean_target_ip,
            
            # The mean destination IP address observed in the session
            'mean_dest_ip': self.mean_dest_ip
        }

        # Return the session data as a JSON object
        return data

    def new_session(self):
        """
        Retrieves a new session message from the JSON I/O system.
        Parses the message to populate the attributes of the current session.
        """
        # Retrieve the session message and response code from jsonIO
        message, code = self.jsonIO.post()

        # If the response code is not 201 (created), exit the method
        if code != 201:
            return

        # Parse the session message to update session attributes
        self.uuid = message['uuid']  # Unique identifier
        self.label = message['label']  # Associated label
        self.median_coordinates = message['median_coordinates']  # Median coordinates
        self.mean_diff_time = message['mean_diff_time']  # Mean time difference
        self.mean_diff_amount = message['mean_diff_amount']  # Mean amount difference
        self.mean_target_ip = message['mean_target_ip']  # Mean target IP address
        self.mean_dest_ip = message['mean_dest_ip']  # Mean destination IP address
