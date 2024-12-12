import pandas as pd
import json

# Supponiamo che tu riceva il seguente JSON con un valore mancante per "latitude"
json_data = '''
[
    {"UUID": "a923-45b7-gh12-8902", "latitude": -72.1385228126357, "longitude": -44.7689488495527},
    {"UUID": "a923-45b7-gh12-416", "latitude": null, "longitude": -65.0068598526314}
]
'''

# Carica il JSON in un oggetto Python (lista di dizionari)
data = json.loads(json_data)

# Converte i dati in un DataFrame
df = pd.DataFrame(data)

# Sostituisce i valori NaN (valori mancanti) con None
df = df.where(pd.notnull(df), None)

# Stampa il DataFrame per verificare il risultato
print(df)
