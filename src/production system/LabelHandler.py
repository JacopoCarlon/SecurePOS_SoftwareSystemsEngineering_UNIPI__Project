import json_io  # Custom module for handling JSON input/output operations

class LabelHandler:
    """
    A class to handle labels and send them to different phases.

    Attributes:
    -----------
    uuid : str
        The unique identifier for the label.
    label : str
        The content of the label.

    Methods:
    --------
    __init__(label):
        Initializes the LabelHandler object with the given label data.

    send_label(phase='evaluation'):
        Sends the label to the specified phase (evaluation or production).
    """

    def __init__(self, label):
        """
        Constructs all the necessary attributes for the LabelHandler object.

        Parameters:
        -----------
        label : dict
            A dictionary containing 'uuid' and 'label' keys.
        """
        # Unique identifier for the label
        self.uuid = label['uuid']
        
        # Content or value of the label
        self.label = label['label']

    def send_label(self, phase='evaluation'):
        """
        Sends the label to the specified phase.

        Parameters:
        -----------
        phase : str, optional
            The phase to send the label to (default is 'evaluation').

        Sends the label to either the evaluation or production system based on the phase.
        """
        # Prepare the message to be sent
        message = {'uuid': self.uuid, 'label': self.label}
        
        if phase == 'evaluation':
            # Send the label to the evaluation phase
            json_io.jsonIO().send_message(message)
        else:
            # Send the label to the production system
            json_io.jsonIO().send_message(message)
