from productionSystemController import ProductionSystemController
from json_io import FlaskServer
import threading
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

    time.sleep(5)  # Attendi che il server Flask sia avviato

    # Create a new production system controller thread
    production_system_thread = threading.Thread(target=start_production_system_controller)
    production_system_thread.start()

    # Wait for both threads to complete
    production_system_thread.join()
    flask_thread.join()

if __name__ == "__main__":
    main()




