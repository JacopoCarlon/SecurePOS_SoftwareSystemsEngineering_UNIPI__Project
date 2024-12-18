from productionSystemController import ProductionSystemController
from json_io import FlaskServer
import threading
import os
import time

def start_flask_server():
    flask_server = FlaskServer()
    flask_server.start()

def start_production_system_controller():
    production_system_controller = ProductionSystemController()
    production_system_controller.run()

def main():
    # Create a new Flask server thread
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.start()

    # Create a new production system controller thread
    production_system_thread = threading.Thread(target=start_production_system_controller)
    production_system_thread.start()

    try:
        # Wait for both threads to complete
        production_system_thread.join()
        flask_thread.join()
    finally:
        # When both threads end, remove the model
        model_path = os.path.join('src', 'production system', 'model', 'classifier_model.joblib')
        if os.path.exists(model_path):
            os.remove(model_path)
            print(f"Removed file: {model_path}")
        else:
            print(f"File not found: {model_path}")

if __name__ == "__main__":
    main()




