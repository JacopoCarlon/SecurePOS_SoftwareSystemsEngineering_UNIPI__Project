import os
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import json

class ModelUpload(Resource):
    def post(self):
        # Debug print per tracciare dettagli della richiesta
        print("Headers:", request.headers)
        print("Content-Type:", request.content_type)
        print("Method:", request.method)
        print("Request Files:", request.files)

        # Verifica se il file è presente nella richiesta
        if 'file' in request.files:
            file = request.files['file']
            print("File received:", file.filename)

            #se il file non esiiste lo crea
            if not os.path.exists(os.path.join('src', 'production system', 'model')):
                os.makedirs(os.path.join('src', 'production system', 'model'))
            
            # Controllo dell'estensione del file
            file.save(os.path.join('src', 'production system', 'model', 'classifier_model.joblib'))
            return {'message': 'Model saved successfully'}, 201
        else:
            return {'error': 'No file part in the request'}, 400

class SessionUpload(Resource):
    def post(self):
        # Gestione dati JSON
        if request.is_json:
            json_data = request.get_json()
            
            # Assicurati che esista la directory per le sessioni
            os.makedirs('session', exist_ok=True)
            
            # Salva i dati della sessione
            filename = json_data.get('uuid', 'default')
            with open(os.path.join('src', 'production system', 'session', filename + ".json"), 'w') as file:
                json.dump(json_data, file)
            return {'message': 'Session saved'}, 201
        
        else:
            print("Unsupported content type")
            return {'error': 'Unsupported media type'}, 415

class FlaskServer:
    def __init__(self):
        print("Server initialized")

        self.app = Flask(__name__)
        CORS(self.app)  # Aggiungi supporto CORS
        self.api = Api(self.app)
        self.api.add_resource(ModelUpload, '/upload_model')
        self.api.add_resource(SessionUpload, '/upload_session')
        
        # Configura Flask per accettare file di grandi dimensioni
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    def start(self):
        """Metodo per avviare il server Flask."""
        print("Starting server")
        self.app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    server = FlaskServer()
    server.start()