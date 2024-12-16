import ClassifierModelController  # Module for handling the classifier model
import PrepareSessionHandler  # Module for managing session preparation
import LabelHandler  # Module for handling labels
import time

# Class to control the production system workflow
class ProductionSystemController:

    def __init__(self):

        print("PORCACCIA LA MADONNA")
        self.classifier = None
        self.session = None

    def handle_classifier_model_deployment(self):
        """
        Initializes and deploys the classifier model.
        
        This method creates an instance of the ClassifierModelController, which is responsible
        for loading and managing the classifier model used for classification tasks.
        """
        print("ciao")
        self.classifier = ClassifierModelController.ClassifierModelController()

    def handle_prepared_session_reception(self):
        """
        Receives a new session using the session handler.
        
        This method initializes the PrepareSessionHandler and uses it to retrieve a new session message.
        The session is then stored for further classification tasks.
        """
        print("ciao1")
        self.session.new_session()

        

    def run_classsification_task(self):
        print("ciao2")
        """
        Performs classification on the session request.
        
        This method takes the session's request, classifies it using the classifier model,
        and initializes a LabelHandler with the resulting label for further processing.
        """
        # Perform classification on the session request using the classifier model
        label = self.classifier.classify(self.session.session_request())
        self.label = LabelHandler.LabelHandler(self.session.uuid, label)
        
        # Initialize a label handler with the classification label
        time.sleep(10)

    def send_label(self):
        print("ciao3")
        """
        Sends the label generated from classification.
        
        This method sends the generated label to the appropriate system (either evaluation or production).
        """
        self.label.send_label()

    def send_label_evaluation(self):
        print("ciao4")
        """
        Sends an evaluation label.
        
        This method specifically sends a label with the phase set to 'evaluation', indicating
        that this label is meant for evaluation purposes rather than production.
        """
        self.label.send_label('evaluation')

    def run(self):
        print("ciaorrrrun")
        """
        Starts the production system workflow.
        
        This method is the main loop of the production system. It continuously handles incoming sessions,
        classifies them using the classifier, and sends the resulting labels to the appropriate system.
        """
        self.classifier = ClassifierModelController.ClassifierModelController()  # Initialize classifier model controller
        self.session = PrepareSessionHandler.PrepareSessionHandler()  # Initialize session handler
        try:
            while True:
                # Continuously handle incoming sessions and classify them
                self.handle_prepared_session_reception()
                
                time.sleep(3)
                self.run_classsification_task()
                #self.send_label()
        except Exception as e:
            # Handle system exit gracefully
            print(f"An error occurred: {e}")
            print("Exiting the production system")
            time.sleep(5)
            exit(-1)
            #os.remove(os.path.join('src', 'production system', 'model', 'classifier_model.joblib'))

    def classify_data(self, data):
        try:
            result = self.classifier_controller.classify(data)
            return result
        except Exception as e:
            return {'error': str(e)}

    print("siamo qui per aso")

# if __name__ == "__main__":
#    print("CRISTO MADONNA")
#    prod = ProductionSystemController()
#    prod.run()
