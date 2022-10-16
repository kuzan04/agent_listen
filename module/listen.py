import socket
import mysql.connector
import ssl
import os
import json
from threading import Thread
from module import log, file, db

class SSLServer:
    def __init__(self, path, host, port, server_cert, server_key, client_cert, config, chunk_size=(1024**2)):
        self._path = path
        self.host = host
        self.port = port
        self.init = config[0:-7]
        self.history = self.init[-1]
        self.chunk_size = chunk_size
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)
        #self._status = {"AG1":0,"AG2":0,"AG3":0,"AG4":0}
        #self._cli = {"AG1":[], "AG2":[], "AG3":[], "AG4":[]}

    def connect(self, log):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen()
            print(f"[LISTENING] Server is listening on {self.host}")
            try:
                while True:
                    conn, _ = sock.accept()
                    with self._context.wrap_socket(conn, server_side=True) as sconn:
                        self._recv(sconn, log)
            except KeyboardInterrupt:
                print("\nCaught keyboard interrupt, exiting")
            finally:
                self.close(sock)

    def find_set_match(_set, _str, i):
        if i == len(_set):
            return -1
        elif _set[i][2] != _str:
            return find_set_match(_set, _str, (i+1))
        elif _set[i][2] == _str:
            return i

    def find_tuple(self, _tuple, mark, c, i):
        if i == len(_tuple):
            return -1
        elif _tuple[i][1] == mark and _tuple[i][-1] == c:
            return _tuple[i]
        else:
            return self.find_tuple(_tuple, mark, c, (i+1))

    def _recv(self, sock, manage):
        while True:
            msg = sock.recv(self.chunk_size).decode()
            if msg:
                if "|" in msg and "#" not in msg:
                    msg = msg.split("|")
                    msg = "|".join(msg[0:-1])
                    msg = msg.split('|')
                    sock.send(db.testConnect(msg[0], msg[1], msg[2], msg[-2], msg[-1]).connect().encode("utf-8"))
                elif "#" in msg:
                    cur_manage = manage.cursor()
                    cur_manage.execute("SELECT pam.agm_id, pam.agm_name, pas.code FROM TB_TR_PDPA_AGENT_MANAGE as pam JOIN TB_TR_PDPA_AGENT_STORE as pas ON pam.ags_id = pas.ags_id;")
                    res_manage = cur_manage.fetchall()
                    table_history = self.history.split(":")[0]
                    column_history = self.history.split(":")[-1]
                    status = db.status(self.init[1], self.init[2], self.init[3], self.init[4]).get()
                    msg_conv = msg.split("#")
                    msg_detail = msg_conv[-1].split("|||")
                    if status[msg_conv[0]] == 1 and msg_conv[0] == "AG1": # Success
                        mark = msg_detail.pop(0)
                        log.Log0Hash(self.init[1], self.init[2], self.init[3], self.init[4], self.init[-4], msg_detail).insertDataHash()
                        selected = self.find_tuple(res_manage, mark, "AG1", 0)
                        cur_manage.execute(f"INSERT INTO {table_history} ({column_history}) VALUE ({selected[0]})")
                        manage.commit()
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG2": # Success.
                        mark, _ = msg_detail.pop(0), msg_detail.pop()
                        file.fileDirectory(self.init[1], self.init[2], self.init[3], self.init[4], self.init[-3], self.init[5], self.init[6:-4], msg_detail).insertDataFile()
                        selected = self.find_tuple(res_manage, mark, "AG2", 0)
                        cur_manage.execute(f"INSERT INTO {table_history} ({column_history}) VALUE ({selected[0]})")
                        manage.commit()
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG3": # Success.
                        mark = msg_detail.pop(0)
                        db.DBcheck(self.init[1], self.init[2], self.init[3], self.init[4], self.init[-2], msg_detail).connect() #self.init[-2:-1]
                        selected = self.find_tuple(res_manage, mark, "AG3", 0)
                        cur_manage.execute(f"INSERT INTO {table_history} ({column_history}) VALUE ({selected[0]})")
                        manage.commit()
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG4": # Success.
                        pass
                    else:
                        pass
                elif "!CHECK" in msg:
                    print("Ok")
                elif "!DISCONNECT" in msg:
                    self.close(sock)
            else:
                break

    def close(self, sock):
        #sock.shutdown(socket.SHUT_RDWR)
        sock.close()

class SSLServerThread(Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        self.daemon = True

    def run(self):
        try:
            self._server.connect(mysql.connector.connect(host=self.init[1], user=self.init[2], password=self.init[3], database=self.init[4], auth_plugin = "mysql_native_password"))
        except Exception:
            pass
