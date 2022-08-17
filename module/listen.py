import socket
import ssl
from threading import Thread

class SSLServer:
    def __init__(self, host, port, server_cert, server_key, client_cert, chunk_size=1024):
        self.host = host
        self.port = port
        self.chunk_size = chunk_size
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
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

    def _recv(self, sock):
        while True:
            data = sock.recv(self.chunk_size)
            if data:
                print(data.decode())
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
