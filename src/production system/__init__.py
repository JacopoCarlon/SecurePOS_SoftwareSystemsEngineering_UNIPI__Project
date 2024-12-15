from productionSystemController import ProductionSystemController
from json_io import FlaskServer
import multiprocessing


def main():


    # Create a new Flask server
    flask_server = FlaskServer()



    # Start the Flask server in a separate process
    flask_process = multiprocessing.Process(target=flask_server.start)
    flask_process.start()

    # Create a new production system controller
    production_system_controller = ProductionSystemController()

    #another process for the production system
    production_system_process = multiprocessing.Process(target=production_system_controller.run)
    production_system_process.start()

    # Wait for the Flask server process to finish
    flask_process.join()
    production_system_process.join()


if __name__ == "__main__":
    main()




