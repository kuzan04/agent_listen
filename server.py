#======================================================
# Package at used
#======================================================
import sys
import socket
import os
import shutil
import time
import datetime
import netifaces as ni
import mysql.connector
from module import cert, listen
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
        if len(CONFIG) < 19:
            print(f"[Errno] Please check file config!!")
            sys.exit(1)
#======================================================
# Set to start listening
#======================================================
def start(local, ip, config, sl):
    reConfig = config[0:-7]
    db_conn = mysql.connector.connect(host=reConfig[1], user=reConfig[2], password=reConfig[3], database=reConfig[4], auth_plugin = "mysql_native_password", sql_mode = 'IGNORE_SPACE')
    server = listen.SSLServer(local, ip, reConfig, sl[0], sl[1], sl[-2], db_conn).connect()
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
    #SERVER=socket.gethostbyname_ex(socket.gethostname())[-1]
    SERVER=ni.ifaddresses('en0')[ni.AF_INET][0]['addr']
    CONFIG=[]
    # of after running
    setConfig(__location__, __ssl__, create, LIST_PATH, CONFIG)
    print("[STARTING] server is starting...")
    #print(CONFIG[10:-7]) # CheckDB
    while SERVER == "127.0.0.1" or SERVER == "localhost" or not(SERVER and SERVER.strip()):
        print("[Errno] Unknow ip ethernet wait for 15 seconds script rebooting.")
        time.sleep(5)
    start(__location__, SERVER, CONFIG, __ssl__)
