import mysql.connector

class Log0Hash:
    def __init__(self, host, user, passwd, db, table, content):
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db
        self.table = table.split(":")
        self._context = content
        self.client = None

    def insertDataHash(self):
        if not self._context == False:
            db = mysql.connector.connect(
                host = self.host,
                user = self.username,
                password = self.password,
                database = self.database,
                auth_plugin = "mysql_native_password"
            )
            if not self._context:
                cursor = db.cursor()
                query = f"INSERT INTO {table[0]} ({table[-1]}) VALUES {tuple(iter(self._context))}"
                cursor.execute(query)
                db.commit()
