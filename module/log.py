import mysql.connector

class Log0Hash:
    def __init__(self, conn, table, content):
        self._connect = conn
        self.table = table.split(":")[0]
        self.column = table.split(":")[-1]
        self._context = content
        self.client = None

    def insertDataHash(self):
        cursor = self._connect.cursor()
        if len(self._context) != 0:
            query = f"INSERT INTO {self.table} ({self.column}) VALUES {tuple(iter(self._context))}"
            cursor.execute(query)
            self._connect.commit()
        else:
            pass
