from productionSystemController import ProductionSystemController
from json_io import FlaskServer
import multiprocessing

if __name__ == "__main__":

    app = ProductionSystemController()
    server = FlaskServer()
    s = multiprocessing.Process(target=app.run)
    s.start()


    # Start the JSON I/O server in a separate process
    p = multiprocessing.Process(target=server.start)  # Cambiato 'run' in 'start'
    p.start()

    # Run the production system controller
