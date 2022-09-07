import mysql.connector
import cx_Oracle
import re
import json
import datetime
import numpy as np

class status:
    def __init__(self, host, user, passwd, db):
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db

    def get(self):
        conn = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database,
            auth_plugin = "mysql_native_password"
        )
        cursor = conn.cursor()
        cursor.execute('SELECT code, status FROM TB_TR_PDPA_AGENT_STORE;')
        return self.convertTupleToSet(cursor.fetchall())

    def convertTupleToSet(self, fetch):
        _status = {}
        for i in fetch:
            _status[i[0]] = i[1]
        return _status

class testConnect:
    def __init__(self, _type, host, user, passwd, db):
        self._type = int(_type)
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db

    def mySql(self):
        try:
            mydb = mysql.connector.connect(
                host = self.host,
                user = self.username,
                password = self.password,
                database = self.database,
                auth_plugin = "mysql_native_password"
            )
            cursor = mydb.cursor()
            cursor.execute('SHOW TABLES;')
            result = cursor.fetchall()
            result = np.asarray(result)
            table = {}
            for i in result:
                cursor.execute(f"SHOW CREATE TABLE {i[0]};")
                res = cursor.fetchall()
                res = np.asarray(res[0])[1].split("\n")
                res.pop(-1)
                name = ""
                for j in range(len(res)):
                    if "KEY" not in res[j]:
                        if j == 0:
                            name = res[j].split("`")[1]
                            table[name] = []
                        else:
                            table[name].append(res[j].split("`")[1])
            return str(json.dumps(table))
        except Exception as e:
            return str(e)

    def oracleDB(self):
        try:
            dsn = cx_Oracle.makedsn(
                self.host,
                "1521",
                service_name=self.database
            )
            myConn = cx_Oracle.connect(
                user = self.username,
                password = self.password,
                dsn=dsn
            )
            c = myConn.cursor()
            c.execute("SELECT table_name FROM all_tables;")
            res = c.fetchall()
            table = []
            for i in res:
                c.execute(f"DESC {i[0]}")
                table.append(f'{c.fetchall()}')
            return str(table)
        except Exception as e:
            return str(e)

    def connect(self):
        if int(self._type) == 1:
            return self.mySql()
        else:
            return self.oracleDB()

class DBcheck:
    def __init__(self, host, user, passwd, db, tb, content):
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db
        self._table = tb
        self.table = []
        self.column = []
        self.val = eval(content[-1])

    def updateMany(self, db, old, new, mark, column, i):
        cursor = db.cursor()
        if i == len(old):
            return 0
        elif i != 0:
            query = f'UPDATE {mark} SET {column[i]} = "{new[i]}" WHERE {column[0]} = {new[0]}'
            cursor.execute(query)
            db.commit()
            return self.updateMany(db, old, new, mark, column, (i+1))
        else:
            return self.updateMany(db, old, new, mark, column, (i+1))

    def upAndDelMany(self, db, _id, new, mark, column, i):
        cursor = db.cursor()
        if i == len(new):
            return 0
        elif new[0] != _id and i != 0:
            query = f'DELETE FROM {mark} WHERE {column[0]} = {_id}'
            cursor.execute(query)
            db.commit()
        elif new[0] == _id and i != 0:
            query = f'UPDATE {mark} SET {column[i]} = "{new[i]}" WHERE {column[0]} = {_id}'
            cursor.execute(query)
            db.commit()
        else:
            return self.upAndDelMany(db, _id, new, mark, column, (i+1))

    def leavings(self, db, _str, result, mark, i):
        cursor = db.cursor()
        if i == len(self.val):
            return 0
        else:
            try:
                if result[i] == self.val[i]:
                    return self.leavings(db, _str, result, mark, (i+1))
                else:
                    query = f"INSERT INTO {self.table[mark]} ({self.column[mark]}) VALUES ({_str})"
                    cursor.execute(query, self.val[i])
                    db.commit()
                    return self.leavings(db, _str, result, mark, (i+1))
            except IndexError:
                query = f"INSERT INTO {self.table[mark]} ({self.column[mark]}) VALUES ({_str})"
                cursor.execute(query, self.val[i])
                db.commit()
                return self.leavings(db, _str, result, mark, (i+1))
            except mysql.connector.errors.IntegrityError as e:
                err = str(e).split(" ")
                if err[0] == "1062" and err[1] == "(23000)":
                    db = mysql.connector.connect(
                        host = self.host,
                        user = self.username,
                        password = self.password,
                        database = self.database,
                        auth_plugin = "mysql_native_password"
                    )
                    return self.leavings(db, _str, result, mark, (i+1))

    def equalSum(self, db, old, mark, column, i, j):
        cursor = db.cursor()
        if i == len(self.val):
            return 0
        elif j == len(self.val[i]):
            return self.equalSum(db, old, mark, column, (i+1), 0)
        elif self.val[i] == old[i] and j != 0:
            query = f'UPDATE {mark} SET {column[j]} = "{self.val[i][j]}" WHERE {column[0]} = {self.val[i][0]}'
            cursor.execute(query)
            db.commit()
            return self.equalSum(db, old, mark, column, i, (j+1))
        elif self.val[i] != old[i] and j != 0:
            cursor.execute(f'DELETE FROM {mark} WHERE {column[0]} = {old[i][0]}')
            db.commit()
            set_str = ["%s" for _ in range(len(column))]
            set_str = ",".join(set_str)
            conv_column = ",".join(column)
            query = f'INSERT INTO {mark} ({conv_column}) VALUES ({set_str})'
            cursor.execute(query, self.val[i])
            db.commit()
            return self.equalSum(db, old, mark, column, (i+1), 0)
        else:
            return self.equalSum(db, old, mark, column, i, (j+1))

    def process(self, db, result, index):
        cursor = db.cursor()
        column = self.column[index].split(",")
        set_str = ["%s" for _ in range(len(column))]
        set_str = ",".join(set_str[:len(set_str)])
        if len(self.val) > len(result) and len(result) == 0:
            query = f"INSERT INTO {self.table[index]} ({self.column[index]}) VALUES ({set_str});"
            cursor.executemany(query, self.val)
            db.commit()
        elif len(self.val) > len(result) and len(result) > 0:
            for i in range(len(result)):
                if self.val[i][0] != result[i][0]:
                    query = f"INSERT INTO {self.table[index]} ({self.column[index]}) VALUES ({set_str})"
                    cursor.execute(query, self.val[i])
                    db.commit()
                else:
                    self.updateMany(db, result[i], self.val[i], self.table[index], column, 0)
                    cursor.execute(f"SELECT {self.column[index]} FROM {self.table[index]};")
                    result = cursor.fetchall()
                    self.leavings(db, set_str, result, index, 0)
        elif len(self.val) == len(result):
            self.equalSum(db, result, self.table[index], column, 0, 0)
        elif len(self.val) < len(result):
            for i in range(len(self.val)):
                if self.val[i] != result[i]:
                    self.upAndDelMany(db, int(result[i][0]), self.val[i], self.table[index], column, 0)
                    cursor.execute(f"SELECT {self.column[index]} FROM {self.table[index]};")
                    result = cursor.fetchall()

    def convertTableToColumn(self):
        for t in self._table:
            self.table.append(t.split(":")[0])
            self.column.append(t.split(":")[-1])

    def connect(self):
        self.convertTableToColumn()
        for i in range(len(self.table)):
            db = mysql.connector.connect(
                host = self.host,
                user = self.username,
                password = self.password,
                database = self.database,
                auth_plugin = "mysql_native_password"
            )
            cursor = db.cursor()
            cursor.execute(f"SELECT {self.column[i]} FROM {self.table[i]};")
            result = cursor.fetchall()
            self.process(db, result, i)
