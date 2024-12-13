from src.db_sqlite3 import DatabaseController
from flask import Flask, request, jsonify
from flask_restful import Resource,Api
import pandas as pd
import json
from src.prepare_system.RawSession import RawSession
import os
import numpy as np



class IngestionSystemOrchestrator():
    def __init__(self):
        #print("sono dentro __init__")
        self.myDB = DatabaseController("myDB.db")
        self.server = "boh"
        self.threshold = 0.4  # da prelevare poi dal file di config
        self.evaluation_phase = False  # da prelevare poi dal file di config
        self.app = Flask(__name__)

        self.app.add_url_rule('/run', methods=['POST'], view_func=self.run)

        if self.init_db():
            print("[INFO] database inizializzato correttamente")
        else:
            print("[ERROR] errore durante inizializzazione del database")


    def init_db(self):
        if os.path.exists("myDB.db"):
            os.remove("myDB.db")
         #   print("DB eliminato")
        myDB = DatabaseController("myDB.db")
        table = """CREATE TABLE IF NOT EXISTS labels 
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                LABEL TEXT DEFAULT NULL
                );"""
        if myDB.create_table(table, []):
            print("tabella LABELS creata correttamente")
        else:
            print("errore creazione tabella")

        table = """ CREATE TABLE IF NOT EXISTS transactionCloud (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                ts1 REAL DEFAULT NULL, ts2 REAL DEFAULT NULL, ts3 REAL DEFAULT NULL, ts4 REAL DEFAULT NULL, ts5 REAL DEFAULT NULL,
                ts6 REAL DEFAULT NULL, ts7 REAL DEFAULT NULL, ts8 REAL DEFAULT NULL, ts9 REAL DEFAULT NULL, ts10 REAL DEFAULT NULL,
                am1 REAL DEFAULT NULL, am2 REAL DEFAULT NULL, am3 REAL DEFAULT NULL, am4 REAL DEFAULT NULL, am5 REAL DEFAULT NULL,
                am6 REAL DEFAULT NULL, am7 REAL DEFAULT NULL, am8 REAL DEFAULT NULL, am9 REAL DEFAULT NULL, am10 REAL DEFAULT NULL
            );"""
        if myDB.create_table(table, []):
            print("tabella TRANSACTION creata correttamente")
        else:
            print("errore creazione tabella")
        table = """CREATE TABLE IF NOT EXISTS localizationSys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                latitude REAL DEFAULT NULL,
                longitude REAL DEFAULT NULL
            );"""
        if myDB.create_table(table, []):
            print("tabella LOCALIZATION  creata correttamente")
        else:
            print("errore creazione tabella")

        table = """
        CREATE TABLE IF NOT EXISTS networkMonitor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                targetIP TEXT DEFAULT NULL,
                destIP TEXT DEFAULT NULL
            );
        """

        if myDB.create_table(table, []):
            print("tabella NETWORK  creata correttamente")
        else:
            print("errore creazione tabella")
        return True

    def ricezioneRecord(self):
        # Ottieni i dati JSON dalla richiesta
        record = request.get_json()

        #print(type(record))
        for key, value in record.items():
            if value is None or value == "" or value == 0:
                record[key] = np.nan

        #print(record)
        if not record:
            print("[ERRORE] mancata ricezione record")
            return jsonify({"error": "Nessun dato ricevuto"}), 400

        # Converti il JSON in un DataFrame pandas
        r = pd.DataFrame(record, index=[0])
        #print(record)

        # Stampa il record ricevuto per debug
        #print(f"[RIC REC] Record ricevuto:\n{r}")

        # Sostituire i valori mancanti (NaN) con None
        r = r.applymap(lambda x: None if pd.isnull(x) else x)  # Questo trasforma NaN in None (NULL per SQLite)

        #print(f"modifica: r = {r}")

        # Controllo dei valori nulli
        if r.isnull().values.any():
            print("[ATTENZIONE] Valori nulli trovati nel record:")
            print(r.isnull().sum())

            # Esempio: Se vuoi sostituire alcuni valori con un default (opzionale)
            # r.fillna({"latitude": 0.0, "longitude": 0.0}, inplace=True)

        # Determina la tabella su cui inserire il record
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
            print("[INFO] posso creare la raw session")
            return True
        else:
            print("[INFO] non posso creare la raw session")
            return False
    def create_raw_session(self, UUID):
        print(f"[INFO] dentro a create raw session")

        obj = RawSession(UUID, self.myDB)
        return obj

    def remove_recordDB(self, UUID):

        print(f"[INFO] dentro la remove_recordDB")
        print(f"uuid = {UUID}")
        query = "DELETE FROM labels WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE]  impossibile eliminare il recod dalla tabella labels")


        query = "DELETE FROM localizationSys WHERE UUID=?"
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
            #print("sono dentro la run")
            record,tabella = self.ricezioneRecord()
            record = pd.DataFrame(record, index=[0]).reset_index(drop=True)
            #print(f"[X] {record}")
            #occhio stampa anche l'indice di riga e me lo mette in UUID

            if self.myDB.insert_dataframe(record,tabella):
                print("[DEBUG] record inserito correttamente nel DB")
            else:
                print("[ERROR] durante l'inserimento del record nel DB")

            if not self.check_raw_session(record["UUID"].values[0]):
                return jsonify({"message": "Dati ricevuti con successo"}), 200
            print("+------------------------------------------------------+")

            r = self.create_raw_session(record["UUID"].values[0]) #posso creare al raw session
            #print(f"type r = {type(r)}")
            #print(r.Rlabels)

            #self.remove_recordDB(record["UUID"].values[0])

            result = r.mark_missing_samples()
            print(f"result mark missing samples {result}")



            if result > self.threshold:
                return #sessione invalida

            if self.evaluation_phase:
                print("ev-->")    #send label
            #hp:raw session sent

            r.correct_missing_samples()
            r.correct_outliers()


            """
            features = r.extract_feature()
            PreparedSession(features)
    
            if development_phase:
                send(segregation_system)
            else:
                send(production_system)
    
            #return msg al client??
            """
            print("*-------------------------------------------------------*")

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











