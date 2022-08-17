import mysql.connector

class Log0Hash:
    def __init__(self, config, content):
        self.host = config[1]
        self.username = config[2]
        self.password = config[3]
        self.database = config[4]
        self.table = config[-2].split(":")
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
