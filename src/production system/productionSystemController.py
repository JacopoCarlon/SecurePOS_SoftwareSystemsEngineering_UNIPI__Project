import ClassifierModelController  # Module for handling the classifier model
import PrepareSessionHandler  # Module for managing session preparation
import LabelHandler  # Module for handling labels
import json_io  # Corrected import for JSON input/output operations
import time

# Class to control the production system workflow
class ProductionSystemController:
    """
    Controller for managing the production system workflow.

    Methods:
    --------
    __init__():
        Initializes the production system controller.
    handle_classifier_model_deployment():
        Initializes and deploys the classifier model.
    handle_prepared_session_reception():
        Receives a new session using the session handler.
    run_classsification_task():
        Performs classification on the session request and initializes a label handler with the classification label.
    send_label():
        Sends the label generated from classification.
    send_label_evaluation():
        Sends an evaluation label.
    run():
        Starts the production system workflow, continuously handling incoming sessions and classifying them.
    """

    def __init__(self):
        """
        Initializes the ProductionSystemController instance.
        
        This constructor sets up any necessary components for the production system.
        Currently, it doesn't perform any specific actions.
        """
        self.jsonIO = json_io.jsonIO()  # Initialize JSON I/O handler

        pass

    def handle_classifier_model_deployment(self):
        """
        Initializes and deploys the classifier model.
        
        This method creates an instance of the ClassifierModelController, which is responsible
        for loading and managing the classifier model used for classification tasks.
        """
        self.classifier = ClassifierModelController.ClassifierModelController()

    def handle_prepared_session_reception(self):
        """
        Receives a new session using the session handler.
        
        This method initializes the PrepareSessionHandler and uses it to retrieve a new session message.
        The session is then stored for further classification tasks.
        """
        self.session = PrepareSessionHandler.PrepareSessionHandler().new_session()

    def run_classsification_task(self):
        """
        Performs classification on the session request.
        
        This method takes the session's request, classifies it using the classifier model,
        and initializes a LabelHandler with the resulting label for further processing.
        """
        print(self.session)
        # Perform classification on the session request using the classifier model
        label = self.classifier.classify(self.session.session_request())
        
        # Initialize a label handler with the classification label
        self.label = LabelHandler.LabelHandler(label)

    def send_label(self):
        """
        Sends the label generated from classification.
        
        This method sends the generated label to the appropriate system (either evaluation or production).
        """
        self.label.send_label()

    def send_label_evaluation(self):
        """
        Sends an evaluation label.
        
        This method specifically sends a label with the phase set to 'evaluation', indicating
        that this label is meant for evaluation purposes rather than production.
        """
        self.label.send_label('evaluation')

    def run(self):
        """
        Starts the production system workflow.
        
        This method is the main loop of the production system. It continuously handles incoming sessions,
        classifies them using the classifier, and sends the resulting labels to the appropriate system.
        """
        #self.handle_classifier_model_deployment()  # Deploy the classifier model
        try:
            while True:
                # Continuously handle incoming sessions and classify them
                self.handle_prepared_session_reception()
                time.sleep(10)

                #self.run_classsification_task()
                #self.send_label()
        except Exception as e:
            # Handle system exit gracefully
            print(f"An error occurred: {e}")
            print("Exiting the production system")

"""
    POST /upload example:
    {
    	"uuid":"test",
    	"label":"test2",
    	"median_coordinates":"1313",
    	"mean_diff_time": "23434",
    	"mean_diff_amount": "23432",
    	"mean_target_ip": "192.168,.1.1",
    	"mean_dest_ip": "192.168.1.1"
    
    }"""