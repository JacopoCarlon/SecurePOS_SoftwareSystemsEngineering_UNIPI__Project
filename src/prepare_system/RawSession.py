import pandas as pd
from src.db_sqlite3 import DatabaseController
import numpy as np
import ipaddress

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
        #print(f"[TMP] Sono dentro la mark missing samples")
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
        pd.set_option('display.max_columns', None)  # Nessun limite al numero di colonne
        pd.set_option('display.width', None)
        #print(f"sono dentro la correct missing samples")

        #correzione timeseries
        self.Rtransaction = self.Rtransaction.applymap(lambda x: np.nan if x is None else x)
        # Visualizza il record delle transazioni
        #print(f"record = \n{self.Rtransaction}")
        #print(f"type of Rtransaction: {type(self.Rtransaction)}")
        ts = self.Rtransaction[['ts1', 'ts2', 'ts3', 'ts4', 'ts5', 'ts6', 'ts7', 'ts8', 'ts9', 'ts10']]
        ts = ts.interpolate(axis=1)
        self.Rtransaction[['ts1', 'ts2', 'ts3', 'ts4', 'ts5', 'ts6', 'ts7', 'ts8', 'ts9', 'ts10']] = ts
        #print(self.Rtransaction)

        #am

        am = self.Rtransaction[['am1', 'am2', 'am3', 'am4', 'am5', 'am6', 'am7', 'am8', 'am9', 'am10']]
        am = am.interpolate(axis=1)
        self.Rtransaction[['am1', 'am2', 'am3', 'am4', 'am5', 'am6', 'am7', 'am8', 'am9', 'am10']] = am
        print(self.Rtransaction)
        #input("...")



        #correzioni attributi statici
        #network
        #print(self.Rnetwork)
        self.Rnetwork = self.Rnetwork.applymap(lambda x: np.nan if x is None else x)

        if self.Rnetwork.shape[0] > 1:
            if pd.isna(self.Rnetwork['targetIP'].iloc[0]):
                self.Rnetwork['targetIP'].iloc[0] = self.Rnetwork['targetIP'].iloc[-1]

            if pd.isna(self.Rnetwork['destIP'].iloc[0]):
                self.Rnetwork['destIP'].iloc[0] = self.Rnetwork['destIP'].iloc[-1]


            self.Rnetwork[['targetIP', 'destIP']] = self.Rnetwork[['targetIP', 'destIP']].fillna(method='ffill')
        #print(self.Rnetwork)

        #loc

        #print(self.Rlocalization)
        self.Rlocalization = self.Rlocalization.applymap(lambda x: np.nan if x is None else x)

        if self.Rlocalization.shape[0] > 1:
            if pd.isna(self.Rlocalization['latitude'].iloc[0]):
                self.Rlocalization['latitude'].iloc[0] = self.Rlocalization['latitude'].iloc[-1]

            if pd.isna(self.Rlocalization['longitude'].iloc[0]):
                self.Rlocalization['longitude'].iloc[0] = self.Rlocalization['longitude'].iloc[-1]

            self.Rlocalization[['latitude', 'longitude']] = self.Rlocalization[['latitude', 'longitude']].fillna(method='ffill')
        print(self.Rlocalization)





    #cpy correct_ouliers
    def correct_outliers(self):
        #print("Dentro la correct outliers")


        # Valori limite
        max_latitude = 90
        min_latitude = -90
        max_long = 180
        min_long = -180

        # Correzione degli outliers
        self.Rlocalization.loc[self.Rlocalization['latitude'] > max_latitude, 'latitude'] = max_latitude
        self.Rlocalization.loc[self.Rlocalization['latitude'] < min_latitude, 'latitude'] = min_latitude

        self.Rlocalization.loc[self.Rlocalization['longitude'] > max_long, 'longitude'] = max_long
        self.Rlocalization.loc[self.Rlocalization['longitude'] < min_long, 'longitude'] = min_long

        print(self.Rlocalization)
        #input("..")
    def extract_features(self):
        #print("sono dentro la extract feature")
        """median_latitude,median_longitude,median_targetIP,median_destIP = 0
        mean_abs_diff_ts = 0
        mean_abs_diff_am = 0
        """
        median_latitude = self.Rlocalization['latitude'].median()
        median_longitude = self.Rlocalization['longitude'].median()

        self.Rnetwork['target'] = self.Rnetwork['targetIP'].apply(lambda x: int(ipaddress.ip_address(x))) #--< occhio
        median_targetIP = self.Rnetwork['target'].median()
        median_targetIP = str(ipaddress.ip_address(int(median_targetIP)))

        self.Rnetwork['dest'] = self.Rnetwork['destIP'].apply(lambda x: int(ipaddress.ip_address(x)))  # --< occhio
        median_destIP = self.Rnetwork['dest'].median()
        median_destIP = str(ipaddress.ip_address(int(median_destIP)))
        print(f"median_latitude = {median_latitude}\t median_longitude = {median_longitude}\nmedian_targetIP = {median_targetIP}\t median_destIP = {median_destIP}")

        self.Rtransaction["mean_abs_diff_ts"] = (abs((self.Rtransaction["ts2"] - self.Rtransaction["ts1"])) + \
                                                (abs(self.Rtransaction["ts3"] - self.Rtransaction["ts2"])) + \
                                                (abs(self.Rtransaction["ts4"] - self.Rtransaction["ts3"])) + \
                                                (abs(self.Rtransaction["ts5"] - self.Rtransaction["ts4"])) + \
                                                (abs(self.Rtransaction["ts6"] - self.Rtransaction["ts5"])) + \
                                                (abs(self.Rtransaction["ts7"] - self.Rtransaction["ts6"])) + \
                                                (abs(self.Rtransaction["ts8"] - self.Rtransaction["ts7"])) + \
                                                (abs(self.Rtransaction["ts9"] - self.Rtransaction["ts8"])) + \
                                                (abs(self.Rtransaction["ts10"] - self.Rtransaction["ts9"])))/9

        self.Rtransaction["mean_abs_diff_am"] = (abs((self.Rtransaction["am2"] - self.Rtransaction["am1"])) + \
                                                (abs(self.Rtransaction["am3"] - self.Rtransaction["am2"])) + \
                                                (abs(self.Rtransaction["am4"] - self.Rtransaction["am3"])) + \
                                                (abs(self.Rtransaction["am5"] - self.Rtransaction["am4"])) + \
                                                (abs(self.Rtransaction["am6"] - self.Rtransaction["am5"])) + \
                                                (abs(self.Rtransaction["am7"] - self.Rtransaction["am6"])) + \
                                                (abs(self.Rtransaction["am8"] - self.Rtransaction["am7"])) + \
                                                (abs(self.Rtransaction["am9"] - self.Rtransaction["am8"])) + \
                                                (abs(self.Rtransaction["am10"] - self.Rtransaction["am9"])))/9
        #print(f"mean_abs_diff_ts = {self.Rtransaction['mean_abs_diff_ts']}")
        #print(f"mean_abs_diff_am = {self.Rtransaction['mean_abs_diff_am']}")
        #print()
        mean_abs_diff_ts = self.Rtransaction['mean_abs_diff_ts'].mean()
        mean_abs_diff_am = self.Rtransaction['mean_abs_diff_am'].mean()

        print(f"finale:\n mean_abs_diff_ts={mean_abs_diff_ts}\t mean_abs_diff_am={mean_abs_diff_am}")
        label = self.Rlabels["LABEL"].mode()[0]
        print(f"label= {label}")



        #input("...")
        features = [mean_abs_diff_ts, mean_abs_diff_am,median_longitude, median_latitude, median_targetIP, median_destIP,label]

        return features



    def correct_missing_samples_bk(self):
        #print(f"sono dentro la correct missing samples")
        self.Rtransaction = self.Rtransaction.applymap(lambda x: np.nan if x is None else x)

        # Visualizza il record delle transazioni
        #print(f"record = \n{self.Rtransaction}")

        # Selezioniamo le colonne `ts1` a `ts10` e creiamo una lista separata per i time series
        ts = []
        for i in range(1, 11):  # ts1-ts10
            ts.append(self.Rtransaction[f"ts{i}"])
        #print(f"tssype = {type(ts)}")

        series = pd.Series(ts)
        interpolated_series = series.interpolate(method='linear')
        #print(interpolated_series)

        interpolated_list = interpolated_series.tolist()
        #print(interpolated_list)

        # Creiamo un DataFrame con i time series
        ts_df = pd.DataFrame(ts).transpose()

        #print(ts_df)
        # Interpolazione lineare sui valori NaN
        ts_df = ts_df.apply(lambda row: row.interpolate(method='linear', axis=0), axis=1)

        # Dopo l'interpolazione, riassegniamo i valori interpolati nel DataFrame originale
        for i in range(1, 11):
            self.Rtransaction[f"ts{i}"] = ts_df[f"ts{i - 1}"]  # Eseguiamo l'aggiornamento per ogni ts

        print(f"DataFrame dopo interpolazione: \n{self.Rtransaction}")

        am_df = pd.DataFrame(am).transpose()
        if ts_df.isnull().values.any():
            #print("entrato")
            ts_df = ts_df.interpolate(method='linear', axis=0, limit_direction='both')
            for i in range(1, 11):
                self.Rtransaction[f"ts{i}"] = ts_df.iloc[:, i - 1]
        if am_df.isnull().values.any():
            #print("entrato")
            am_df = am_df.interpolate(method='linear', axis=0, limit_direction='both')
            for i in range(1, 11):
                self.Rtransaction[f"am{i}"] = am_df.iloc[:, i - 1]

        print(f"[CHECK] risultato dopo l'interpolazione = \n{self.Rtransaction}")


                                                                                    








