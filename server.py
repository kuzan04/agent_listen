#======================================================
# Package at used
#======================================================
import sys
import socket
import threading
import pwd
import grp
import os
from os import walk
from os import listdir
from os.path import isfile, join
import mysql.connector
import re
import json
import datetime
import cx_Oracle
import numpy as np
#======================================================
# Variable global
#======================================================
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
LIST_PATH = os.listdir(__location__)
HEADER=1024
SERVER=socket.gethostbyname_ex(socket.gethostname())[-1]
CONFIG=[]
FORMAT='utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
STATUS={"AG1":0,"AG2":0,"AG3":0,"AG4":0}
CONFIG_CLIENT = {"AG1":[], "AG2":[], "AG3":[], "AG4":[]}
#======================================================
# Settings from config
#======================================================
try:
    if "config" in LIST_PATH:
        __location__ = os.path.join(__location__, LIST_PATH[LIST_PATH.index("config")])
        LIST_PATH = os.listdir(__location__)
        with open(os.path.join(__location__, LIST_PATH[LIST_PATH.index("init.conf")]), "r") as f:
            for i in f.readlines():
                if i.find("#") == -1:
                    x=i.split("=")
                    CONFIG.append(x[1].strip("\n"))
except Exception as e:
    print(str(e))
    sys.exit(1)
#======================================================
# Check config
#======================================================
if len(CONFIG) < 2:
    print(f"[ERROR] Please check file config!!")
    sys.exit(1)
#================== Sub Function ======================
#======================================================
# Find value set match
#======================================================
def find_set_match(_set, _str, i):
    if i == len(_set):
        return -1
    elif _set[i][2] != _str:
        return find_set_match(_set, _str, (i+1))
    elif _set[i][2] == _str:
        return i
#======================================================
# Change value in array of set
#======================================================
def changeValue(_set, new, i):
    if i == len(_set) and i == len(new):
        return -1
    elif _set[i] == new[i]:
        return changeValue(_set, new, (i+1))
    elif _set[i] != new[i]:
        _set[i] = new[i]
        return changeValue(_set, new, (i+1))
#======================================================
# Find array match
#======================================================
def find_match(arr1, arr2):
    for item in arr1:
        if item[1:] == tuple(iter(arr2)):
            return True
        else:
            pass
    return False
#======================================================
# Test connect from app
#======================================================
def testConnection(msg):
    if (int(msg[0]) == 1):
        try:
            mydb = mysql.connector.connect(
                host = msg[1],
                user = msg[2],
                password = msg[-2],
                database = msg[-1],
                auth_plugin = 'mysql_native_password'
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
    elif (int(msg[0]) == 0):
        try:
            dsn = cx_Oracle.makedsn(
                msg[0],
                '1521',
                service_name=msg[-1]
            )
            myconn = cx_Oracle.connect(
                user=msg[1],
                password=msg[-2],
                dsn=dsn
            )
            c = myconn.cursor()
            c.execute('SELECT table_name FROM all_tables;')
            res = c.fetchall()
            table = []
            for i in res:
                c.execute(f'DESC {i[0]}')
                table.append(f'{c.fetchall()}')
            return str(table)
        except Exception as e:
            return str(e)
#================ Process Function ====================
#======================================================
# Client Log0 Hash
#======================================================
def insertDataHash(config, msg):
    if not msg[1] == False:
        client=config[-2].split(":")
        db=mysql.connector.connect(host=config[1], user=config[2], password=config[3], database=config[4], auth_plugin='mysql_native_password')
        if not msg[1]:
            cursor=db.cursor()
            data=msg[1].split("&&&")
            query=f"INSERT INTO {client[0]} ({client[1]}) VALUE {tuple(iter(data))}"
            cursor.execute(query)
            db.commit()
#======================================================
# Client Directory/File
#======================================================
def insertAndCreateFile(config, msg):
    if not msg[1] == False:
        data=msg[1].split("*")
        val = data[0:len(data)-1]
        table=config[-1].split(":")
        conv_columns = table[1].split(",")
        columns = ",".join(conv_columns[1:])
        db=mysql.connector.connect(host=config[1], user=config[2], password=config[3], database=config[4], auth_plugin='mysql_native_password')
        cursor=db.cursor()
        cursor.execute(f"SELECT {table[1]} FROM {table[0]} ORDER BY id ASC")
        result=cursor.fetchall()
        if not os.path.isdir(f"{config[5]}{data[-1]}"):
            uid = pwd.getpwnam(config[6]).pw_uid
            gid = grp.getgrnam(config[7]).gr_gid
            os.mkdir(f"{config[5]}{data[-1]}")
            os.chown(f"{config[5]}{data[-1]}", uid, gid)
        if os.path.isdir(f"{config[5]}{data[-1]}"):
                uid = pwd.getpwnam(config[6]).pw_uid
                gid = grp.getgrnam(config[7]).gr_gid
                os.chown(f"{config[5]}{data[-1]}", uid, gid)
        if len(result) == 0:
                query = f"INSERT INTO {table[0]} ({columns}) VALUES {tuple(iter(val))}"
                cursor.execute(query)
                db.commit()
        else:
            res = True
            res = find_match(result, val)
            if res == False:
                query = f"INSERT INTO {table[0]} ({columns}) VALUES {tuple(iter(val))}"
                cursor.execute(query)
                db.commit()
            _, _, filenames = next(walk(f'{config[5]+data[-1]}'), (None, None, []))
            if not data[-2] in filenames:
                cursor.execute(f'SELECT {table[1]} FROM {table[0]} WHERE name_file = "{data[-2]}"')
                result = cursor.fetchall()
                query = f'DELETE FROM {table[0]} WHERE {conv_columns[0]} = {result[0][0]}'
                cursor.execute(query)
                db.commit()
#======================================================
# Client check query from database
#======================================================
def insertCheckRecord(config, msg):
    if not msg[1] == False:
       split_msg=msg[1].split("&&&")
       data=eval("".join(split_msg[3]))
       columns=split_msg[2].split(',')
       db=mysql.connector.connect(host=config[1], user=config[2], password=config[3], database=config[4], auth_plugin='mysql_native_password')
       cursor=db.cursor()
       cursor.execute(f"SELECT {split_msg[2]} FROM {split_msg[1]}_server")
       result=cursor.fetchall()
       set_str = ["%s" for _ in range(len(columns))]
       conv_set_str = ",".join(set_str[:len(set_str)])
       if len(data) > len(result) and len(result) == 0:
           query=f'INSERT INTO {split_msg[1]}_server ({split_msg[2]}) VALUES ({conv_set_str})'
           cursor.executemany(query, data)
           db.commit()
       elif len(data) > len(result) and len(result) > 0:
           count=0
           for x in range(len(result)):
               if data[x] != result[x]:
                   if data[x][0] != result[x][0]:
                       query=f"INSERT INTO {split_msg[1]}_server ({split_msg[2]}) VALUES ({conv_set_str})"
                       cursor.execute(query, data[x])
                       db.commit()
                       count+=1
                   else:
                       for xy in range(len(result[x])):
                           if xy != 0:
                               query = f'UPDATE {split_msg[1]}_server SET {columns[xy]} = "{data[x][xy]}" WHERE {columns[0]} = {data[x][0]}'
                               cursor.execute(query)
                               db.commit()
               cursor.execute(f"SELECT {split_msg[2]} FROM {split_msg[1]}_server")
               result=cursor.fetchall()
               count+=1
               while count < len(data):
                   query0=f'INSERT INTO {split_msg[1]}_server ({split_msg[2]}) VALUES ({conv_set_str})'
                   cursor.execute(query0, data[count])
                   db.commit()
                   count+=1
       elif len(data) == len(result):
           for x in range(len(data)):
               if data[x] != result[x]:
                   for xy in range(len(data[x])):
                       if xy != 0:
                           query = f'UPDATE {split_msg[1]}_server SET {columns[xy]} = "{data[x][xy]}" WHERE {columns[0]} = {data[x][0]}'
                           cursor.execute(query)
                           db.commit()
       elif len(data) < len(result):
           count=0
           for x in range(len(data)):
               if data[x] != result[x]:
                   if data[x][0] == result[x][0]:
                       for xy in range(len(data[x])):
                           if xy != 0:
                               query = f'UPDATE {split_msg[1]}_server SET {columns[xy]} = "{data[x][xy]}" WHERE {columns[0]} = {result[x][0]}'
                               cursor.execute(query)
                               db.commit()
                               count+=1
                           else:
                               query = f'DELETE FROM {split_msg[1]}_server WHERE {columns[0]} = {result[x][0]}'
                               cursor.execute(query)
                               db.commit()
                               count+=1
                               cursor.execute(f"SELECT {split_msg[2]} FROM {split_msg[1]}_server")
                               db.commit()
                               count+=1
           while count < len(result):
               query = f'DELETE FROM {split_msg[1]}_server WHERE {columns[0]} = {result[count][0]}'
               cursor.execute(query)
               db.commit()
               count+=1
#======================================================
# Set handle get message for client
#======================================================
def handle_client(conn, addr, stu, cli):
    print(f"[NEW CONNECTIONS] {addr} connected.")
    connected = True
    while connected:
        msg_length=conn.recv(HEADER).decode(FORMAT)
        if "|" in msg_length or "&&&" in msg_length or "," in msg_length:
            if "," in msg_length and "&&&" not in msg_length and "|" not in msg_length:
                msg_length = msg_length.split(",")
                conn.recv(int(msg_length[-1])).decode(FORMAT)
                msg = ",".join(msg_length[0:-1])
                msg = msg.split(',')
                stu[msg[0]] = int(msg[1])
                conn.send("recevied.".encode(FORMAT))
                print(stu)
                connected = False
            elif "&&&" in msg_length and "|" not in msg_length:
                msg_length = msg_length.split("&&&")
                conn.recv(int(msg_length[-1])).decode(FORMAT)
                msg = "&&&".join(msg_length[0:-1])
                msg = msg.split("&&&")
                if len(cli) > 0 and len(msg) <= 3:
                    index = find_set_match(cli[msg[0]], msg[1], 0)
                    if msg[-1] == "rm":
                        cli[msg[0]].pop(index)
                        with open(os.path.join(__location__, "config.json"), "w+") as oldfile:
                            json.dump(cli, oldfile, indent = 4)
                    else:
                        cli[msg[0]][index][1] = msg[-1]
                        with open(os.path.join(__location__, "config.json"), "w+") as outfile:
                            json.dump(cli, outfile, indent = 4)
                elif len(cli) > 0 and len(msg) > 3:
                    cli[msg[0]].append(msg)
                    with open(os.path.join(__location__, "config.json"), "w+") as outfile:
                        json.dump(cli, outfile, indent = 4)
                else:
                    if "config.json" in os.listdir(__location__):
                        with open(os.path.join(__location__, "config.json")) as json_file:
                            cli = json.load(json_file)
                connected = False
            elif "," not in msg_length and "&&&" not in msg_length and "|" in msg_length:
                msg_length = msg_length.split("|")
                conn.recv(int(msg_length[-1])).decode(FORMAT)
                msg = "|".join(msg_length[0:-1])
                msg = msg.split('|')
                conn.send(testConnection(msg).encode(FORMAT))
                connected = False
        else:
            msg_length = int(msg_length)
            msg=conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected=False
            elif ("," not in msg or "&&&" not in msg) and "#" in msg:
                msg_conv = msg.split("#")
                msg_detail = msg[1].split("|||")
                print(msg_conv, "\n", msg_detail)
                '''if stu[msg_conv[0]] == 1:
                    insertDataHash(CONFIG, msg_conv)
                elif stu[msg_conv[1]] == 1:
                    insertAndCreateFile(CONFIG, msg_conv)
                elif stu[msg_conv[2]] == 1:
                    insertCheckRecord(CONFIG, msg_conv)
                elif stu[msg_conv[3]] == 1:
                    wakeUpSniffer(CONFIG, msg_conv)'''
    conn.close()
#======================================================
# Set to start listening
#======================================================
def start(stu, cli):
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER[1]}")
    try:
        while True:
            conn, addr=server.accept()
            thread=threading.Thread(target=handle_client, args=(conn, addr, stu, cli))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
       server.close()
#======================================================
#  Start listening
#======================================================
if __name__ == "__main__":
    ADDR = (SERVER[1], int(CONFIG[0]))
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    print("[STARTING] server is starting...")
    start(STATUS, CONFIG_CLIENT)
