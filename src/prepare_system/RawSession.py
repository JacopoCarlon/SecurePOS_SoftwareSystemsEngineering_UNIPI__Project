import pandas as pd
from src.db_sqlite3 import DatabaseController
class RawSession():
    def __init__(self,UUID,myDB):
        query = "SELECT * FROM labels WHERE UUID=?"
        self.Rlabels = myDB.read_sql(query, [UUID])

        query = "SELECT * FROM networkMonitor WHERE UUID=?"
        self.Rnetwork = myDB.read_sql(query, [UUID])

        query = "SELECT * FROM localizationSys WHERE UUID=?"
        self.Rlocalization = myDB.read_sql(query, [UUID])

        query = "SELECT * FROM transactionCloud WHERE UUID=?"
        self.Rtransaction = myDB.read_sql(query, [UUID])

    def mark_missing_samples(self):
        records = [self.Rlabels,self.Rnetwork,self.Rtransaction,self.Rlocalization]
        count_null = 0
        count_elem = 0
        for record in enumerate(records):
            count_elem = count_elem + record.size
            count_null = count_null + record.isna().sum().sum()
            record = record.fillna(-1)
        return count_null/count_elem
   # def correct_missing_samples(self):








