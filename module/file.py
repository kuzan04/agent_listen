import pwd
import grp
import os
from os import walk
from os import listdir
from os.path import isfile, join
import mysql.connector

class fileDirectory:
    def __init__(self, host, user, passwd, db, tb, col, val, main, _dir, uftp, gftp):
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db
        self.table = tb
        self.column = col
        self.value = val
        self.directory = _dir
        self.file = file
        self.uftp = uftp
        self.gftp = gftp

    def find_match(self, arr, arr0, i):
        if i == len(arr):
            return False
        elif arr[i][1:] == tuple(iter(arr0)):
            return True
        else:
            return self.find_match(arr, arr0, (i+1))

    def createFile(self, result):
        if not os.path.isdir(f"{_dir}"):
            uid = pwd.getpwnam(self.uftp).pw_uid
            gid = grp.getgrname(self.gftp).gr_uid
            os.mkdir(f"{_dir}")
            os.chown(f"{_dir}", uid, gid)
        elif os.path.isdir(f"{_dir}"):
            uid = pwd.getpwnam(self.uftp).pw_uid
            gid = grp.getgrname(self.gftp).gr_uid
            os.chown(f"{_dir}", uid, gid)

    def insert(self):
        db = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database,
            auth_plugin = "mysql_native_password"
        )
        cursor = db.cursor()
        cursor.execute(f"SELECT {table[-1]} FROM {table[0]} ORDER BY id ASC;")
        result = cursor.fetchall()
        self.createFile()
        if len(result) == 0:
            query = f"INSERT INTO {self.table} ({self.column}) VALUES {tuple(iter(self.val))}"
            cursor.execute(query)
            db.commit()
        else:
            res = True
            if self.find_match(result, val, 0) == False:
                query = f"INSERT INTO {self.table} ({self.column}) VALUES {tuple(iter(self.val))}"
                cursor.execute(query)
                db.commit()
                _, _, filenames = next(walk(f"{self.directory}"), (None, None, []))
                if not file in filenames:
                    cursor.execute(f'SELECT {column} FROM {table} WHERE name_file = "{file}"')
                    result = cursor.fetchall()
                    _id = self.column.split(",")[0]
                    query = f'DELETE FROM {table} WHERE {_id} = "{result[0][0]}"'
                    cursor.execute(query)
                    db.commit()
