import mysql.connector

class Log0Hash:
    def __init__(self, host, user, passwd, db, table, content):
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db
        self.table = table.split(":")[0]
        self.column = table.split(":")[-1]
        self._context = content
        self.client = None

    def insertDataHash(self):
        db = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database,
            auth_plugin = "mysql_native_password"
        )
        cursor = db.cursor()
        if len(self._context) != 0:
            query = f"INSERT INTO {self.table} ({self.column}) VALUES {tuple(iter(self._context))}"
            cursor.execute(query)
            db.commit()
        else:
            pass
