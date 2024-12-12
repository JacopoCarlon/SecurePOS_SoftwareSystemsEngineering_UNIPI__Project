import csv
import requests
import time

# Configurazione dell'endpoint del server REST
ingestion_system_url = "http://127.0.0.1:5001/run"


# Funzione per leggere i dati da un file CSV
def read_csv(file_path):
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Errore: il file '{file_path}' non esiste.")
    except csv.Error as e:
        print(f"Errore durante la lettura del file CSV: {e}")
    return data


# Funzione per inviare un record al sistema di ingestion
def send_record(record):
    try:
        response = requests.post(ingestion_system_url, json=record)
        if response.status_code == 200:
            print(f"Dati inviati con successo: {record}")
        else:
            print(f"Errore nell'invio: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Errore di connessione: {e}")


if __name__ == "__main__":
    # File CSV da cui prelevare i dati
    csv_files = [
        "data/localizationSys.csv",
        "data/networkMonitor.csv",
        "data/labels.csv",
        "data/transactionCloud.csv"
    ]

    # Legge i dati da ciascun file CSV
    datasets = [read_csv(file) for file in csv_files]

    # Controlla che ci siano dati validi
    if not all(datasets):
        print("Uno o più file CSV non contengono dati validi. Controlla i file.")
    else:
        print("Inizio invio dei dati in maniera ciclica.")

        # Calcola il numero massimo di righe tra i file
        max_rows = max(len(dataset) for dataset in datasets)

        # Invio ciclico delle righe
        for i in range(max_rows):
            for dataset_index, dataset in enumerate(datasets):
                if i < len(dataset):  # Controlla se esiste una riga nel dataset     corrente
                    #print(f"[CLIENT] dataset = {dataset}")
                    record = dataset[i]
                    print(f"Inviando riga {i} del file {csv_files[dataset_index]}...")
                    # print(f"[CLIENT] record = {record}")
                    send_record(record)
            time.sleep(1)  # Pausa tra i cicli per evitare invii troppo rapidi
