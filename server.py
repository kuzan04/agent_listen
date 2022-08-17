#======================================================
# Package at used
#======================================================
import sys
import socket
import os
import shutil
import time
import datetime
import subprocess
from module import cert, listen, log, file, db
#======================================================
# Settings from config
#======================================================
def setConfig(__location__, __ssl__, create, LIST_PATH, CONFIG):
    try:
        if "config" in LIST_PATH:
            __config__ = os.path.join(__location__, LIST_PATH[LIST_PATH.index("config")])
            LIST_PATH = os.listdir(__config__)
            ssl_path = os.path.join(__config__, "ssl")
            with open(os.path.join(__config__, LIST_PATH[LIST_PATH.index("init.conf")]), "r") as f:
                for i in f.readlines():
                    if i.find("#") == -1:
                        x=i.split("=")
                        CONFIG.append(x[1].strip("\n"))
            if "ssl" not in LIST_PATH:
                for i in create:
                    cert.createCert(CONFIG[-7:], i).gen()
                    os.mkdir(ssl_path)
                for i in range(len(__ssl__)):
                    shutil.move(os.path.join(__location__, __ssl__[i]), os.path.join(ssl_path, __ssl__[i]))
                    __ssl__[i] = os.path.join(ssl_path, __ssl__[i])
            else:
                for i in range(len(__ssl__)):
                    __ssl__[i] = os.path.join(ssl_path, __ssl__[i])
    except Exception as e:
        print(str(e))
        sys.exit(1)
    finally:
        if len(CONFIG) < 18:
            print(f"[ERROR] Please check file config!!")
            sys.exit(1)
#======================================================
# Set to start listening
#======================================================
def start(stu, cli, sl):
    server = listen.SSLServer(SERVER[-1], int(CONFIG[0]), sl[0], sl[1], sl[-2]).connect()
    s_thread = listen.SSLServerThread(server)
    s_thread.start()
#======================================================
# Start listen
#======================================================
if __name__ == "__main__":
    # setting file location
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    __ssl__ = ["listen.crt", "listen.key", "client.crt", "client.key"]
    create = ["listen", "client"]
    LIST_PATH = os.listdir(__location__)
    # setting socket
    HEADER=1024
    SERVER=socket.gethostbyname_ex(socket.gethostname())[-1]
    CONFIG=[]
    FORMAT='utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"
    # of after running
    STATUS={"AG1":0,"AG2":0,"AG3":0,"AG4":0}
    CONFIG_CLIENT = {"AG1":[], "AG2":[], "AG3":[], "AG4":[]}
    setConfig(__location__, __ssl__, create, LIST_PATH, CONFIG)
    print("[STARTING] server is starting...")
    #print(CONFIG[10:-7]) # CheckDB
    start(STATUS, CONFIG_CLIENT, __ssl__)
