import socket
import time
from message import create_request_msg, create_release_msg, parse_msg
from config import MESSAGE_SIZE

class Process:
    def __init__(self, process_id, host, port):
        self.process_id = process_id
        self.host = host
        self.port = port

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def request_access(self):
        request_msg = create_request_msg(self.process_id)
        self.socket.sendall(request_msg.encode())
        grant_msg = self.socket.recv(MESSAGE_SIZE).decode().strip()
        msg_type, granted_process_id = parse_msg(grant_msg)

        if msg_type == "GRANT" and granted_process_id == self.process_id:
            print(f"[{self.process_id}] Acesso à região crítica concedido.")
            return True
        else:
            print(f"[{self.process_id}] Acesso à região crítica negado.")
            return False


    def release_access(self):
        release_msg = create_release_msg(self.process_id)
        self.socket.sendall(release_msg.encode())
        print(f"[{self.process_id}] Acesso à região crítica liberado.")

    def run(self):
        self.connect()

        while True:
            time.sleep(1)  # Simula trabalho fora da região crítica
            if self.request_access():
                time.sleep(1)  # Simula trabalho na região crítica
                self.release_access()

