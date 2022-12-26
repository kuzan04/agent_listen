#import os
#import sys
import mysql.connector
import cx_Oracle
import json
import numpy as np


class status:
    def __init__(self, conn):
        self._connect = conn

    def get(self):
        cursor = self._connect.cursor()
        cursor.execute('SELECT code, status FROM TB_TR_PDPA_AGENT_STORE')
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
            cursor.execute('SHOW TABLES')
            result = cursor.fetchall()
            table = {}
            try:
                result = [x[0].decode('utf-8') for x in result]
                for i in result:
                    cursor.execute(f"SHOW CREATE TABLE {i}")
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
            except (UnicodeDecodeError, AttributeError):
                result = np.asarray(result)
                for i in result:
                    cursor.execute(f"SHOW CREATE TABLE {i[0]}")
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
            finally:
                return str(json.dumps(table))
        except Exception as e:
            return str(e)

    def oracleDB(self):
        '''if sys.platform == 'linux' or sys.platform == 'linux2':
            cx_Oracle.init_oracle_client(config_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), "config/instantclient_19_10_ARM64"))
        elif sys.platform == 'win32':
            cx_Oracle.init_oracle_client(config_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), "config/instantclient_21_8_x86_64"))'''
        try:
            dsn = cx_Oracle.makedsn(
                self.host,
                "1521",
                service_name=self.database
            )
            myConn = cx_Oracle.connect(
                user=self.username,
                password=self.password,
                dsn=dsn,
                encoding="UTF-8"
            )
            c = myConn.cursor()
            c.execute("SELECT table_name FROM user_tables")
            res = c.fetchall()
            table = {}
            for i in res:
                c.execute(f'SELECT * FROM {i[0]}')
                col = [c[0] for c in c.description]
                table[i[0]] = col
            return str(json.dumps(table))
        except Exception as e:
            return str(e)

    def connect(self):
        if int(self._type) == 1:
            return self.mySql()
        else:
            return self.oracleDB()


class DBCheck:
    def __init__(self, conn, tb, content):
        self._connect = conn
        self._from = content[0]
        self.table = tb.split(":")[0]
        self.column = tb.split(":")[-1]
        self.val = eval(content[-1])

    def equalSum(self, old, i, a):
        if i == len(self.val):
            return a
        else:
            _old = list(old[i])
            _old.pop() 
            _old[0] = int(_old[0])
            _old_ = tuple(_old)
            if self.val[i] == _old_:
                return self.equalSum(old, (i+1), a)
            elif self.val[i] != _old_:
                print(self.val[i], _old_)
                a.append(i)
                return self.equalSum(old, (i+1), a)
            else:
                pass

    def insertMore(self, old, column, i):
        cursor = self._connect.cursor()
        try:
            if i == len(self.val):
                return -1
            elif old[i] == self.val[i]:
                return self.insertMore(old, column, (i+1))
            else:
                self.update(old, i, column.split(","), 0)
                return self.insertMore(old, column, (i+1))
        except IndexError:
                if i == len(self.val):
                    return -1
                else:
                    val = self.val[i]+(self._from,)
                    val = list(val)
                    val = [str(x) for x in val]
                    val = tuple(val)
                    query = f"INSERT INTO {self.table} ({column}) VALUE {val}"
                    cursor.execute(query)
                    self._connect.commit()
                    return self.insertMore(old, column, (i+1))

    def update(self, old, mark, column, i):
        cursor = self._connect.cursor()
        val = self.val[mark]+(self._from,)
        val = list(val)
        val = [str(x) for x in val]
        val = tuple(val)
        try:
            if i == len(old):
                return -1
            elif old[mark][0] == val[0] and old[mark][i] != val[i] and i != 0:
                query = f'UPDATE {self.table} SET {column[i]} = "{val[i]}" WHERE {column[0]} = {val[0]} AND {column[-1]} = "{self._from}"'
                cursor.execute(query)
                self._connect.commit()
                return self.update(old, mark, column, (i+1))
            elif old[mark][0] != val[0]:
                '''column = ",".join(column)
                query = f'INSERT INTO {self.table} ({column}) VALUE {val}'
                cursor.execute(query)
                self._connect.commit()'''
            else:
                return self.update(old, mark, column, (i+1))
        except IndexError:
            print('indexError')
            '''column = ",".join(column)
            query = f'INSERT INTO {self.table} ({column}) VALUE {val}'
            cursor.execute(query)
            self._connect.commit()'''

    def delete(self, old, column, i, j):
        cursor = self._connect.cursor()
        conv_column = ",".join(column)
        try:
            if len(old) != 0:
                if i == len(self.val):
                    return i
                else:
                    val = self.val[i] + (self._from,)
                    val = list(val)
                    val = [str(x) for x in val]
                    val = tuple(val)
                    cursor.execute(f'SELECT {conv_column} FROM {self.table} WHERE {column[0]} = "{val[0]}" AND {column[-1]} = "{self._from}"')
                    mark = cursor.fetchall()
                    if j == len(val):
                        return self.delete(old, column, (i+1), j)
                    elif old[i][j] != val[j] and j == 0:
                        if len(mark) > 1:
                            cursor.execute(f'SELECT id FROM {self.table} WHERE {column[0]} = "{val[0]}" AND {column[-1]} = "{self._from}" ORDER BY id ASC')
                            _id = cursor.fetchall()
                            for y in range(len(_id)):
                                if y != len(_id):
                                    query = f'DELETE FROM {self.table} WHERE id = "{_id[0]}"'
                                    cursor.execute(query)
                                    self._connect.commit()
                                else:
                                    pass
                        return self.delete(old, column, (i+1), j)
                    elif old[i][j] == val[j] and j != 0:
                        query = f'UPDATE {self.table} SET {column[j]} = "{val[j]}" WHERE {column[0]} = {old[i][0]} AND {column[-1]} = "{self._from}"'
                        cursor.execute(query)
                        self._connect.commit()
                        return self.delete(old, column, i, (j+1))
                    else:
                        return self.delete(old, column, (i+1), j)
            else:
                return 0
        except IndexError:
            return -1

    def overSize(self, column, i):
        cursor = self._connect.cursor()
        if i == len(self.val):
            return -1
        else:
            val = self.val[i] + (self._from,)
            val = list(val)
            val = [str(x) for x in val]
            val = tuple(val)
            conv_column = column.split(",")
            cursor.execute(f'SELECT {column} FROM {self.table} WHERE {conv_column[0]} = "{val[0]}" AND {conv_column[-1]} = "{self._from}"')
            mark = cursor.fetchall()
            if len(mark) == 0:
                cursor.execute(f"INSERT INTO {self.table} ({column}) VALUE {val}")
                self._connect.commit()
            return self.overSize(column, (i+1))

    def connect(self):
        cursor = self._connect.cursor()
        column = self.column.split(",")
        set_str = ["%s" for _ in range(len(self.val[0])+1)]
        set_str = ",".join(set_str)
        truly_column = ",".join(column[0:len(self.val[0])]) + f",{column[-1]}"
        # Statement(2) UP
        cursor.execute(f'SELECT {truly_column} FROM {self.table} WHERE {column[-1]} = "{self._from}"')
        res = cursor.fetchall()
        self._connect.commit()
        if len(res) == 0:
            query = f"INSERT INTO {self.table} ({truly_column}) VALUES ({set_str})"
            self.val = [x+(self._from,) for x in self.val]
            cursor.executemany(query, self.val)
            self._connect.commit()
        elif len(res) < len(self.val):
            print(res, "\n", self.val)
            #self.insertMore(res, truly_column, 0)
        elif len(res) == len(self.val):
            current_index = self.equalSum(res, 0, [])
            if current_index is not None:
                for i in current_index:
                    self.update(res, i, column, 0)
        elif len(res) > len(self.val):
            print(res, "\n", self.val)
            '''count = 0
            again = self.delete(res, truly_column.split(","), 0, 0)
            while again >= 50:
                count+=1
                again = self.delete(res[(again*count):], truly_column.split(","), 0, 0)
            else:
                if again == 0:
                    self.overSize(truly_column, 0)
                else:
                    pass'''
