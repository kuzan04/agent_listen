import pwd
import grp
import os
from os import walk
from os import listdir
from os.path import isfile, join
import mysql.connector

class fileDirectory:
    def __init__(self, host, user, passwd, db, tb, _dir, cftp, val):
        self.host = host
        self.username = user
        self.password = passwd
        self.database = db
        self.table = tb.split(":")[0]
        self.column = tb.split(":")[-1]
        self.directory = _dir
        self.uftp = cftp[0]
        self.gftp = cftp[-1]
        self.value = val

    def find_match(self, arr, i):
        if i == len(arr):
            return False
        elif arr[i][1:] == tuple(iter(self.value)):
            return True
        else:
            return self.find_match(arr, (i+1))

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

    def findNameFile(self, re, a_file, i):
        if i == len(a_file):
            return re
        else:
            return self.findNameFile(re+a_file[i].split("@")[-1]+"@", a_file, (i+1))

    def insertDataFile(self):
        db = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.database,
            auth_plugin = "mysql_native_password"
        )
        cursor = db.cursor()
        cursor.execute(f"SELECT {self.column} FROM {self.table} ORDER BY id ASC;")
        result = cursor.fetchall()
        #self.createFile()
        columns = ",".join(self.column.split(",")[1:])
        if len(result) == 0:
            query = f"INSERT INTO {self.table} ({columns}) VALUES {tuple(iter(self.value))}"
            cursor.execute(query)
            db.commit()
        else:
            res = True
            if self.find_match(result, 0) == False:
                query = f"INSERT INTO {self.table} ({columns}) VALUES {tuple(iter(self.value))}"
                cursor.execute(query)
                db.commit()
            _, _, filenames = next(walk(f"{self.directory}"), (None, None, []))
            reverse = self.findNameFile("", filenames, 0).split("@")
            reverse.pop()
            if not self.value[-1] in reverse:
                cursor.execute(f'SELECT {self.column} FROM {self.table} WHERE name_file = "{self.value[-1]}"')
                result = cursor.fetchall()
                _id = self.column.split(",")[0]
                query = f'DELETE FROM {self.table} WHERE {_id} = "{result[0][0]}"'
                cursor.execute(query)
                db.commit()
