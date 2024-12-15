from src.db_sqlite3 import DatabaseController
from flask import Flask, request, jsonify
import pandas as pd
import json
from src.prepare_system.RawSession import RawSession
from src.prepare_system.IngestionSystemConfig import IngConfiguration
from src.prepare_system.PreparedSession import PreparedSession
import os
import numpy as np


# Variabile globale per il conteggio dei file generati
i = 0

class IngestionSystemOrchestrator():
    def __init__(self):
        """
        Inizializza il sistema di orchestrazione. Carica la configurazione,
        crea un'istanza del controller del database,
        imposta il server Flask e inizializza il database.
        """
        self.myDB = DatabaseController("myDB.db")

        # Variabile per il server di destinazione (placeholder, da configurare)
        self.server = "boh"
        self.ingestion_system_config = IngConfiguration()

        # Parametri di configurazione

        print(f"threshold = {self.ingestion_system_config.threshold}\t ev_phase {self.ingestion_system_config.evaluation_phase}\t "
              f"devphsase = {self.ingestion_system_config.development_phase}")

        # Configurazione del server Flask
        self.app = Flask(__name__)

        # Aggiunge il route per il metodo run
        self.app.add_url_rule('/run', methods=['POST'], view_func=self.run)

        # Inizializza il database
        if self.init_db():
            print("[INFO] database inizializzato correttamente")
        else:
            print("[ERROR] errore durante inizializzazione del database")

    def init_db(self):
        """
        Inizializza il database eliminando eventuali file esistenti e creando le tabelle necessarie.
        """
        # Rimuove il database esistente, se presente
        if os.path.exists("myDB.db"):
            os.remove("myDB.db")

        myDB = DatabaseController("myDB.db")
        # Creazione della tabella labels
        table = """CREATE TABLE IF NOT EXISTS labels 
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                UUID TEXT,
                LABEL TEXT DEFAULT NULL
                );"""
        if myDB.create_table(table, []):
            print("tabella LABELS creata correttamente")
        else:
            print("errore creazione tabella")

        # Creazione della tabella transactionCloud
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

        # Creazione della tabella localizationSys
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

        # Creazione della tabella networkMonitor
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
        """
        Riceve un record JSON dalla richiesta HTTP POST e lo converte in un DataFrame pandas.
        """
        # Ottieni i dati JSON dalla richiesta
        record = request.get_json()

        # Sostituisci valori nulli o vuoti con NaN
        for key, value in record.items():
            if value is None or value == "" or value == 0:
                record[key] = np.nan

        if not record:
            print("[ERRORE] mancata ricezione record")
            return jsonify({"error": "Nessun dato ricevuto"}), 400

        # Converti il JSON in un DataFrame pandas
        r = pd.DataFrame(record, index=[0])

        # Trasforma i valori NaN in None per compatibilità con SQLite
        r = r.applymap(lambda x: None if pd.isnull(x) else x)

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

    def check_raw_session(self, UUID):
        """
        Verifica se sono presenti tutti i record necessari per creare una raw session.
        """
        query = """
                select * from labels as lb
                inner join localizationSys as ls on ls.UUID=lb.UUID 
                inner join networkMonitor as nm on nm.UUID=ls.UUID
                inner join transactionCloud as tc on tc.UUID=nm.UUID 
                where lb.UUID =?
                """

        result = self.myDB.read_sql(query, [UUID])
        if result.shape[0] > 0:
            print("[INFO] inizio creazione della raw session")
            return True
        else:
            return False

    def create_raw_session(self, UUID):
        """
        Crea una raw session utilizzando i dati presenti nel database.
        """
        obj = RawSession(UUID, self.myDB)
        return obj

    def remove_recordDB(self, UUID):
        """
        Rimuove i record associati a un UUID specifico da tutte le tabelle del database.
        """
        query = "DELETE FROM labels WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE] impossibile eliminare il record dalla tabella labels")

        query = "DELETE FROM localizationSys WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE] impossibile eliminare il record dalla tabella localizationsSys")

        query = "DELETE FROM networkMonitor WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE] impossibile eliminare il record dalla tabella networkMonitor")

        query = "DELETE FROM transactionCloud WHERE UUID=?"
        if not self.myDB.delete(query, [UUID]):
            print("[ERRORE] impossibile eliminare il record dalla tabella transactionCloud")

    def run(self):
        """
        Gestisce la ricezione e l'elaborazione di un record JSON inviato tramite POST.
        Controlla se è possibile creare una raw session e, se valida, estrae le caratteristiche.
        """
        try:
            record, tabella = self.ricezioneRecord()
            record = pd.DataFrame(record, index=[0]).reset_index(drop=True)

            # Inserisce il record nel database
            if self.myDB.insert_dataframe(record, tabella):
                print("[DEBUG] record inserito nel DB")
            else:
                print("[ERROR] durante l'inserimento del record nel DB")

            # Controlla se è possibile creare una raw session
            if not self.check_raw_session(record["UUID"].values[0]):
                return jsonify({"message": "Dati ricevuti con successo"}), 200

            UUID = record["UUID"].values[0]
            r = self.create_raw_session(UUID)

            # Rimuove i record dal database
            self.remove_recordDB(UUID)

            # Valida e corregge i dati
            result = r.mark_missing_samples()
            if result > self.ingestion_system_config.threshold:
                return  # Sessione invalida

            if self.ingestion_system_config.evaluation_phase:
                print("ev-->")  # Placeholder per invio etichetta

            r.correct_missing_samples()
            r.correct_outliers()

            features = r.extract_features()

            global i
            s = PreparedSession(features, UUID)
            record = s.to_dict()
            my_json = json.dumps(record)

            with open(f'lore/data{i}.json', 'w') as f:
                f.write(my_json + '\n')
            i += 1

            print("*-------------------------------------------------------*")
            #input("...")
            return jsonify({"message": "Dati ricevuti con successo"}), 200

        except Exception as e:
            print(f"Errore durante l'elaborazione: {e}")
            return jsonify({"error": "Errore durante l'elaborazione"}), 500

    def r(self, host="127.0.0.1", port=5001, debug=True):
        """
        Avvia il server Flask.
        """
        print("[INFO] Avvio del server Flask...")
        self.app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    orc = IngestionSystemOrchestrator()
    orc.r()
