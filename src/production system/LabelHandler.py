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

    def __init__(self, uuid, label):
        """
        Constructs all the necessary attributes for the LabelHandler object.

        Parameters:
        -----------
        label : dict
            A dictionary containing 'uuid' and 'label' keys.
        """
        # Unique identifier for the label
        self.label = f'''{{"session_id": "{uuid}", 
                        "source": "production", 
                        "value": "{label}"}}'''
        

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

        print("Sending label", self.label)
        

