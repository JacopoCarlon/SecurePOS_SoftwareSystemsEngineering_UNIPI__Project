import pandas as pd
from src.db_sqlite3 import DatabaseController

class RawSession():
    def __init__(self,UUID,myDB):
        query = "SELECT UUID,LABEL FROM labels WHERE UUID=?"
        self.Rlabels = myDB.read_sql(query, [UUID])

        query = "SELECT UUID, targetIP,destIP FROM networkMonitor WHERE UUID=?"
        self.Rnetwork = myDB.read_sql(query, [UUID])

        query = "SELECT UUID,latitude,longitude FROM localizationSys WHERE UUID=?"
        self.Rlocalization = myDB.read_sql(query, [UUID])

        query = "SELECT UUID,ts1,ts2,ts3,ts4,ts5,ts6,ts7,ts8,ts9,ts10,am1,am2,am3,am4,am5,am6,am7,am8,am9,am10 FROM transactionCloud WHERE UUID=?"
        self.Rtransaction = myDB.read_sql(query, [UUID])

    def mark_missing_samples(self):
        print(f"[TMP] Sono dentro la mark missing samples")
        records = [self.Rlabels, self.Rnetwork, self.Rtransaction, self.Rlocalization]

        count_null = 0
        count_elem = 0
        for record in records:
            count_elem += record.size  # Conteggio elementi totali
            count_null += record.isna().sum().sum()  # Conteggio valori nulli totali
            record.isnull()
            record.empty

            # Modifica dei valori nulli
            #record.fillna(-1, inplace=True)  # OCCHIO forse conviene lasciarlo NULL

        missing_ratio = count_null / count_elem if count_elem > 0 else 0
        print(f"[INFO] Percentuale valori mancanti: {missing_ratio * 100:.2f}%")
        return missing_ratio

    def correct_missing_samples(self):
        print(f"sono dentro la correct missing samples")
        # correzione  time series sample
        for record in self.Rtransaction:
            print(f"record = {record}")
            ts = []
            am = []
            for i in range(1, 11):  # ts1-ts10 e am1-am10
                ts.append(record[f"ts{i}"])
                am.append(record[f"am{i}"])

            ts_df = pd.DataFrame(ts).transpose()
            am_df = pd.DataFrame(am).transpose()
            if ts_df.isnull().values.any():
                print("entrato")
                ts_df = ts_df.interpolate(method='linear', axis=0, limit_direction='both')
                for i in range(1, 11):
                    record[f"ts{i}"] = ts_df.iloc[:, i - 1]
            if am_df.isnull().values.any():
                print("entrato")
                am_df = am_df.interpolate(method='linear', axis=0, limit_direction='both')
                for i in range(1, 11):
                    record[f"am{i}"] = am_df.iloc[:, i - 1]
            print(f"[CHECK] risultato dopo l'interpolazione = \n{result}")
        # fine for grande che cicla nel caso in cui ci siano più transazioni con il solito UUID










