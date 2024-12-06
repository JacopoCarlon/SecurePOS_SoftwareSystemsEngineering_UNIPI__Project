import ClassifierModelController
import PrepareSessionHandler
import ClassifierModelController
import LabelHandler
import jsonIO

class ProductionSystemController:
    def __init__(self):
        pass

    def handle_classifier_model_deployment(self):

        self.classifier = ClassifierModelController.classifierModelController()

        pass


    def handle_prepared_session_reception(self):
        #receive the session
        self.session = PrepareSessionHandler.PrepareSessionHandler().new_session()


    def run_classsification_task(self):
        #classify the session
        label = self.classifier.classify(self.session.session_request())
        self.label = LabelHandler.LabelHandler(label)

        pass


    def send_label(self):
        self.label.send_label()
        pass

    def send_label_evaluation(self):
        self.label.send_label('evaluation')
        pass

    def run(self):
        self.handle_classifier_model_deployment()
        try:
            while True:
                self.handle_prepared_session_reception()
                self.run_classsification_task()
                self.send_label()
        except:
            print("Exiting the production system")