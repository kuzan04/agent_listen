import socket
import ssl
import os
import json
from threading import Thread
from module import log, file, db

class SSLServer:
    def __init__(self, path, host, port, server_cert, server_key, client_cert, config, chunk_size=2048):
        self._path = path
        self.host = host
        self.port = port
        self.init = config[0:-7]
        self.chunk_size = chunk_size
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)
        #self._status = {"AG1":0,"AG2":0,"AG3":0,"AG4":0}
        #self._cli = {"AG1":[], "AG2":[], "AG3":[], "AG4":[]}

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen()
            print(f"[LISTENING] Server is listening on {self.host}")
            try:
                while True:
                    conn, _ = sock.accept()
                    with self._context.wrap_socket(conn, server_side=True) as sconn:
                        self._recv(sconn)
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

    def _recv(self, sock):
        while True:
            msg = sock.recv(self.chunk_size).decode()
            if msg:
                if "|" in msg and "#" not in msg:
                    msg = msg.split("|")
                    msg = "|".join(msg[0:-1])
                    msg = msg.split('|')
                    sock.send(db.testConnect(msg[0], msg[1], msg[2], msg[-2], msg[-1]).connect().encode("utf-8"))
                elif "#" in msg:
                    status = db.status(self.init[1], self.init[2], self.init[3], 'DOL_PDPA').get()
                    msg_conv = msg.split("#")
                    msg_detail = msg_conv[-1].split("|||")
                    if status[msg_conv[0]] == 1 and msg_conv[0] == "AG1": # Success
                        msg_detail.pop(0)
                        log.Log0Hash(self.init[1], self.init[2], self.init[3], self.init[4], self.init[-3], msg_detail).insertDataHash()
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG2": # Success.
                        msg_detail.pop(0), msg_detail.pop()
                        file.fileDirectory(self.init[1], self.init[2], self.init[3], self.init[4], self.init[-2], self.init[5], self.init[6:-3], msg_detail).insertDataFile()
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG3":
                        db.DBcheck(self.init[1], self.init[2], self.init[3], self.init[4]. self.init[-1:], msg_detail).connect()
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG4":
                        pass
                    else:
                        pass
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
            self._server.connect()
        except Exception:
            pass

'''if "&&&" in msg and "|" not in msg:
    msg = msg.split("&&&")
    msg = "&&&".join(msg[0:-1])
    msg = msg.split("&&&")
    if len(self._cli[msg[0]]) > 0 and len(msg) <= 3:
        index = self.find_set_match(self._cli[msg[0]], msg[1], 0)
        if msg[-1] == "rm":
            self._cli[msg[0]].pop(index)
            with open(os.path.join(self._path, "config.json"), "w+") as oldfile:
                json.dump(self._cli, oldfile, indent = 4)
                sock.send("removed.".encode(self._format))
        else:
            self._cli[msg[0]][index][1] = msg[-1]
            with open(os.path.join(self._path, "config.json"), "w+") as outfile:
                json.dump(self._cli, outfile, indent = 4)
    elif len(self._cli[msg[0]]) > 0 and len(msg) > 3:
        self._cli[msg[0]].append(msg)
        with open(os.path.join(self.path, "config.json"), "w+") as outfile:
            json.dump(self._cli, outfile, indent = 4)
    else:
        if "config.json" in os.listdir(self._path):
            with open(os.path.join(self._path, "config.json")) as json_file:
                self._cli = json.load(json_file)'''
