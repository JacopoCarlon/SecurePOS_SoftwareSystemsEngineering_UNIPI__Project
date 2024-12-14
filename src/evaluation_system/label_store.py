"""
    Module for interaction with labels' DataBase (creation, push/pop)
"""
import logging
from db_sqlite3 import DatabaseController


class LabelStore:
    """
    Class for general interaction with label DB
    """

    def __init__(self):
        self.db = DatabaseController('evaluationDB.db')

    def ls_store_label_df(self, label, table):
        """
        Insert label_dataframe object into target table of DataBase
        :param label: Dataframe Label object
        :param table: Target Table in DB
        :return:
        """
        if not self.db.insert_dataframe(label, table):
            logging.error("Impossible to <insert_dataframe>, in table : {%s}", table)
            raise ValueError("Evaluation System label storage failed")

    def ls_create_table(self, query, params=None):
        """
        :param query: query to create table
        :param params: params to insert in placeholders in query
        :return: False if any error has occurred, True otherwise
        """
        if not self.db.create_table(query, params):
            logging.error("Impossible to <create> the table with :"
                          "\nquery : {%s}}", query)
            raise ValueError("Evaluation System create_table failed")

    def ls_delete_labels(self, query, params=None):
        """
        :param query: query to delete labels
        :param params: params to insert in placeholders in query
        :return: nothing, can raise errors
        """
        if not self.db.delete(query, params):
            logging.error("Impossible to <delete> the table with :"
                          "\nquery : {%s}}", query)
            raise ValueError("Evaluation System delete_labels failed")

    def ls_select_labels(self, query, params=None):
        """
        :param query: query to select labels
        :param params: params to insert in placeholders in query
        :return: dataframe
        """
        return self.db.read_sql(query, params)
