import mysql.connector

# global dict to reuse previous results
pre_rs = dict()


class DB:

    def __init__(self, d):
        self.cnx = mysql.connector.connect(user='root', password='rootPass', host='localhost', use_pure=True, database=d)
        # print("DB: connection established")

    def close_conn(self):
        self.cnx.close()

    @staticmethod
    def clear_history():
        # reset the pre_rs
        global pre_rs
        pre_rs = dict()

    def run(self, query):

        global pre_rs

        if query in pre_rs:
            # print("DEBUG: reuse query")
            return pre_rs[query]

        cursor = self.cnx.cursor()
        cursor.execute(query)
        result_set = cursor.fetchall()
        # print(query, "\t", len(result_set))
        cursor.close()

        pre_rs[query] = result_set

        return result_set
