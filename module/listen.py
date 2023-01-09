import socket
import ssl
from threading import Thread
from itertools import chain
from module import log, file, db

class SSLServer:
    def __init__(self, path, host, config, server_cert, server_key, client_cert, connect, chunk_size=(1024**2)):
        self._path = path
        self.host = host
        self.init = config
        self.port = int(self.init[0])
        self._connect = connect
        self.history = self.init[-1]
        self.chunk_size = chunk_size
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)

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

    def find_tuple(self, _tuple, mark, c, i):
        if i == len(_tuple):
            return -1
        elif _tuple[i][1] == mark and _tuple[i][-1] == c:
            return _tuple[i]
        else:
            return self.find_tuple(_tuple, mark, c, (i+1))

    def find_tuple1(self, _t, a, i):
        if i == len(a):
            return -1
        elif list(_t)[0] == a[i]:
            return i
        else:
            return self.find_tuple1(_t, a, (i+1))

    def _recv(self, sock):
        while True:
            msg = sock.recv(self.chunk_size).decode()
            if msg:
                if "|" in msg and "#" not in msg:
                    msg = msg.split("|")
                    msg = "|".join(msg)
                    msg = msg.split('|')
                    sock.send(db.testConnect(msg[0], msg[1], msg[2], msg[-2], msg[-1]).connect().encode("utf-8"))
                elif "#" in msg:
                    cur_manage = self._connect.cursor()
                    cur_manage.execute("SELECT pam.agm_id, pam.agm_name, pas.code FROM TB_TR_PDPA_AGENT_MANAGE as pam JOIN TB_TR_PDPA_AGENT_STORE as pas ON pam.ags_id = pas.ags_id;")
                    res_manage = cur_manage.fetchall()
                    self._connect.commit()
                    table_history = self.history.split(":")[0]
                    column_history = self.history.split(":")[-1]
                    status = db.status(self._connect).get()
                    msg_conv = msg.split("#")
                    msg_detail = msg_conv[-1].split("|||")
                    selected = ()
                    if status[msg_conv[0]] == 1 and msg_conv[0] == "AG1":
                        mark = msg_detail.pop(0)
                        log.Log0Hash(self._connect, self.init[-4], msg_detail).insertDataHash()
                        selected = self.find_tuple(res_manage, mark, "AG1", 0)
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG2":
                        mark, _ = msg_detail.pop(0), msg_detail.pop()
                        file.fileDirectory(self._connect, self.init[-3], self.init[5], self.init[6:-4], msg_detail).insertDataFile()
                        selected = self.find_tuple(res_manage, mark, "AG2", 0)
                    elif status[msg_conv[0]] == 1 and msg_conv[0] == "AG3":
                        mark = msg_detail.pop(0)
                        db.DBCheck(self._connect, self.init[-2], msg_detail).connect()
                        selected = self.find_tuple(res_manage, mark, "AG3", 0)
                    else:
                        pass
                    cur_manage.execute('SELECT agm_id FROM TB_TR_PDPA_AGENT_LISTEN_HISTORY GROUP BY agm_id;')
                    find_history = [list(x) for x in cur_manage.fetchall()]
                    find_history = list(chain.from_iterable(find_history))
                    idx = self.find_tuple1(selected, find_history, 0)
                    if idx == -1:
                        cur_manage.execute(f"INSERT INTO {table_history} ({column_history}) VALUE ({selected[0]})")
                        self._connect.commit()
                    else:
                        cur_manage.execute(f"UPDATE {table_history} SET _get_ = NOW() WHERE {column_history[0]} = {find_history[idx]};")
                        self._connect.commit()
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
            self._server.connect()
        except Exception:
            pass
