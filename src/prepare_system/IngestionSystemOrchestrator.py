from src.db_sqlite3 import DatabaseController
from flask import Flask, request, jsonify
from flask_restful import Resource,Api
import pandas as pd
from src.prepare_system.RawSession import RawSession
import os



class IngestionSystemOrchestrator():
    def __init__(self):
        print("sono dentro __init__")
        self.myDB = DatabaseController("myDB.db")
        self.server = "boh"
        self.threshold = 0.4  # da prelevare poi dal file di config
        self.evaluation_phase = False  # da prelevare poi dal file di config
        self.app = Flask(__name__)

        self.app.add_url_rule('/run', methods=['POST'], view_func=self.run)
        """
        if self.init_db():
            print("[INFO] database inizializzato correttamente")
        else:
            print("[ERROR] errore durante inizializzazione del database")
        """

    def init_db(self):
        if os.path.exists("myDB.db"):
            os.remove("myDB.db")
            print("DB eliminato")
        myDB = DatabaseController("myDB.db")
        table = """CREATE TABLE IF NOT EXISTS labels 
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                LABEL TEXT
                );"""
        if myDB.create_table(table, []):
            print("tabella LABELS creata correttamente")
        else:
            print("errore creazione tabella")

        table = """ CREATE TABLE IF NOT EXISTS transactionCloud (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                ts1 REAL, ts2 REAL, ts3 REAL, ts4 REAL, ts5 REAL,
                ts6 REAL, ts7 REAL, ts8 REAL, ts9 REAL, ts10 REAL,
                am1 REAL, am2 REAL, am3 REAL, am4 REAL, am5 REAL,
                am6 REAL, am7 REAL, am8 REAL, am9 REAL, am10 REAL
            );"""
        if myDB.create_table(table, []):
            print("tabella TRANSACTION creata correttamente")
        else:
            print("errore creazione tabella")
        table = """CREATE TABLE IF NOT EXISTS localizationSys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                latitude REAL,
                longitude REAL
            );"""
        if myDB.create_table(table, []):
            print("tabella LOCALIZATION  creata correttamente")
        else:
            print("errore creazione tabella")

        table = """
        CREATE TABLE IF NOT EXISTS networkMonitor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                targetIP TEXT,
                destIP TEXT
            );
        """

        if myDB.create_table(table, []):
            print("tabella NETWORK  creata correttamente")
        else:
            print("errore creazione tabella")
        return True
    def ricezioneRecord(self):
        record = request.get_json()
        if not record:
            print("[ERRORE] mancata ricezione record")
            return jsonify({"error": "Nessun dato ricevuto"}), 400

        r = pd.DataFrame(record, index=[0])
        tabella = "errore"
        if "LABEL" in record:
            tabella = "labels"
        elif "latitude" in record:
            tabella = "localizationSys"
        elif "targetIP" in record:
            tabella = "networkMonitor"
        elif "ts1" in record:
            tabella = "transactionCloud"
        return r, tabella

    def check_raw_session(self,UUID):
        query = """
                select * from labels as lb
                inner join localizationSys as ls on ls.UUID=lb.UUID 
                inner join networkMonitor as nm on nm.UUID=ls.UUID
                inner join transactionCloud as tc on tc.UUID=nm.UUID 
                where lb.UUID =?
                """
        result = self.myDB.read_sql(query, [UUID]) #vedo se ci sono tutti i record per comporre una sessione
        if result.shape[0] > 0:
            return True
        else:
            return False
    def create_raw_session(self, UUID, myDB):
        obj = RawSession(UUID, myDB)
        return obj
    def remove_recordDB(self, UUID):
        query = "DELETE FROM labels WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE]  impossibiile eliminare il recod dalla tabella labels")


        query = "DELETE FROM localizationsSys WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE]  impossibiile eliminare il recod dalla tabella localizationsSys")

        query = "DELETE FROM networkMonitor WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE]  impossibiile eliminare il recod dalla tabella networkMonitor")

        query = "DELETE FROM transactionCloud WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE]  impossibiile eliminare il recod dalla tabella transactionCloud")


    def run(self):
        try:
            print("sono dentro la run")
            record,tabella = self.ricezioneRecord()
            """
            self.myDB.insert(record,tabella)
    
            if not self.check_raw_session(record["UUID"]):
                # forse devo dire al client che ho ricevuto i dati
                return
    
            r = self.create_raw_session(record["UUID"]) #posso creare al raw session
            self.remove_recordDB(record["UUID"])
            result = r.mark_missing_samples()
            if result > self.threshold:
                return #sessione invalida
            if self.evaluation_phase:
                print("ev-->")    #send label
            #hp:raw session sent
            
            r.correct_missing_samples()
            r.correct_ouliers()
            features = r.extract_feature()
            PreparedSession(features)
    
            if development_phase:
                send(segregation_system)
            else:
                send(production_system)
    
            #return msg al client??
            """
            return jsonify({"message": "Dati ricevuti con successo"}), 200

        except Exception as e:
            print(f"Errore durante l'elaborazione: {e}")
            return jsonify({"error": "Errore durante l'elaborazione"}), 500

    def r(self,host="127.0.0.1", port=5001, debug=True):
        print("[INFO] Avvio del server Flask...")
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    print("sono dentro il main")
    orc = IngestionSystemOrchestrator()
    orc.r()











