import os
import shutil
from os import walk

class fileDirectory:
    def __init__(self, conn, tb, _dir, cftp, val):
        self._connect = conn
        self.table = tb.split(":")[0]
        self.column = tb.split(":")[-1]
        self.directory = _dir
        self._lpath = cftp[0]
        self._dpath = cftp[-1]
        self.value = val

    def find_match(self, arr, i):
        if i == len(arr):
            return False
        elif arr[i][1:] == tuple(iter(self.value)):
            return True
        else:
            return self.find_match(arr, (i+1))

    def findNameFile(self, re, a_file, i):
        if i == len(a_file):
            return re
        else:
            return self.findNameFile(re+a_file[i].split("@")[-1]+"@", a_file, (i+1))

    def insertDataFile(self):
        cursor = self._connect.cursor()
        cursor.execute(f"SELECT {self.column} FROM {self.table} ORDER BY id ASC;")
        result = cursor.fetchall()
        columns = ",".join(self.column.split(",")[1:])
        _, _, filenames = next(walk(f"{self.directory}"), (None, None, []))
        if len(result) == 0:
            query = f"INSERT INTO {self.table} ({columns}) VALUES {tuple(iter(self.value))}"
            cursor.execute(query)
            self._connect.commit()
        elif self.find_match(result, 0) == False and len(result) > 0:
            query = f"INSERT INTO {self.table} ({columns}) VALUES {tuple(iter(self.value))}"
            cursor.execute(query)
            self._connect.commit()
        else:
            reverse = self.findNameFile("", filenames, 0).split("@")
            reverse.pop()
            if not self.value[-1] in reverse:
                _id = self.column.split(",")[0]
                query = f'UPDATE {self.table} SET _get = NOW() WHERE {_id} = "{result[0][0]}"'
                cursor.execute(query)
                self._connect.commit()
        self.moveToMain(filenames, 0)

    def moveToMain(self, filenames, i):
        if i == len(filenames):
            return -1
        else:
            if filenames[i] != ".DS_Store":
                convert_filename = filenames[i].split("@")
                if convert_filename[0] == "AG2" and filenames[i] in os.listdir(self.directory) and convert_filename[-1].split(".")[-1] == "log":
                    shutil.move(f"{self.directory}{filenames[i]}", f"{self._lpath}{filenames[i]}")
                    return self.moveToMain(filenames, (i+1))
                elif convert_filename[0] == "AG2" and filenames[i] in os.listdir(self.directory) and convert_filename[-1].split(".")[-1] in ["csv", "xlsx", "xls"]:
                    shutil.move(f"{self.directory}{filenames[i]}", f"{self._dpath}{filenames[i]}")
                    return self.moveToMain(filenames, (i+1))
                else:
                    return self.moveToMain(filenames, (i+1))
            else:
                return self.moveToMain(filenames, (i+1))
