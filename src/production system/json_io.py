import os
from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS
import json

class jsonIO(Resource):
    def post(self):
        # Debug print per tracciare dettagli della richiesta
        print("Headers:", request.headers)
        print("Content-Type:", request.content_type)
        print("Method:", request.method)
        print("Request Files:", request.files)

        #stampo il contenuto del file
        if 'file' in request.files:
            file = request.files['file']
            print("File content:", file.read())

        # Gestione upload file .joblib
        if 'file' in request.files:
            file = request.files['file']
            
            # Controllo dell'estensione del file
            if file.filename.endswith('.joblib'):
                # Assicurati che esista la directory per i modelli
                os.makedirs('model', exist_ok=True)
                
                # Salva il file
                file.save(os.path.join('model', file.filename))
                return {'message': 'Model saved successfully'}, 201
            else:
                return {'error': 'Only .joblib files are allowed'}, 400

        # Gestione dati JSON
        elif request.is_json:
            json_data = request.get_json()
            print("Request JSON:", json_data)
            
            # Assicurati che esista la directory per le sessioni
            os.makedirs('session', exist_ok=True)
            
            # Salva i dati della sessione
            filename = json_data.get('uuid', 'default')
            with open(os.path.join('session', filename + ".json"), 'w') as file:
                json.dump(json_data, file)
            return {'message': 'Session saved'}, 201
        
        else:
            print("Unsupported content type")
            return {'error': 'Unsupported media type'}, 415

class FlaskServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Aggiungi supporto CORS
        self.api = Api(self.app)
        self.api.add_resource(jsonIO, '/')
        
        # Configura Flask per accettare file di grandi dimensioni
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    def start(self):
        """Metodo per avviare il server Flask."""
        self.app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    server = FlaskServer()
    server.start()