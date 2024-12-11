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
        print(f"[TMP] sono dentro la mark missing samples")
        print(f"Rlabels : {self.Rlabels}")
        print(f"RNetwork: {self.Rnetwork}")
        print(f"Rtrans: {self.Rtransaction}")
        print(f"Rloc : {self.Rlocalization}")
        print(f"type of Rlabels {type(self.Rlabels)}")


        records = [self.Rlabels, self.Rnetwork, self.Rtransaction, self.Rlocalization]
        count_null = 0
        count_elem = 0
        for record in records:
            count_elem = count_elem + record.size
            count_null = count_null + record.isna().sum().sum()
            record.fillna(-1)
        return count_null/count_elem

    def correct_missing_samples(self):
        print(f"sono dentro la correct missing samples")










