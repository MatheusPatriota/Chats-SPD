import socket
import threading
from message import create_grant_msg, parse_msg
from config import MESSAGE_SIZE

class Coordinator:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.queue = []

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"[COORDINATOR] Ouvindo em {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            thread.start()

    def handle_client(self, client_socket, address):
        print(f"[NEW CONNECTION] {address} conectado.")
        
        while True:
            msg = client_socket.recv(MESSAGE_SIZE).decode().strip()
            msg_type, process_id = parse_msg(msg)

            if msg_type is None or process_id is None:
                continue

            if msg_type == "REQUEST":
                self.queue.append((client_socket, process_id))
                if len(self.queue) == 1:
                    grant_msg = create_grant_msg(process_id)
                    self.queue[0][0].sendall(grant_msg.encode())

            elif msg_type == "RELEASE":
                if self.queue and self.queue[0][1] == process_id:
                    self.queue.pop(0)
                    if self.queue:
                        grant_msg = create_grant_msg(self.queue[0][1])
                        self.queue[0][0].sendall(grant_msg.encode())
