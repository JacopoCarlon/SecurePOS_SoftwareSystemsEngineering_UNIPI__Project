import subprocess
import time


def run_client():
    time.sleep(4)  # Aspetta che il sistema di ingestion sia pronto
    subprocess.run(["python", "client.py"])

if __name__ == "__main__":
    # Avvia il sistema di ingestion in un sottoprocesso
    ingestion_process = subprocess.Popen(["python", "IngestionSystemOrchestrator.py"])

    try:
        # Avvia il client
        run_client()
    finally:
        # Termina il processo di ingestion
        ingestion_process.terminate()
