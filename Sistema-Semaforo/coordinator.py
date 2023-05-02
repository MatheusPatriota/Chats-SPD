import socket
import threading
import time
from message import Message
import sys
class Coordinator:
    def __init__(self, port):
        self.port = port
        self.queue = []
        self.process_counters = {}
        self.lock = threading.Lock()

    def handle_request(self, addr, process_id):
        with self.lock:
            self.queue.append((addr, process_id))
            self.process_counters[process_id] = self.process_counters.get(process_id, 0) + 1

    def handle_release(self, process_id):
        with self.lock:
            for idx, (_, p_id) in enumerate(self.queue):
                if p_id == process_id:
                    self.queue.pop(idx)
                    break

    def process_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(("localhost", self.port))

            while True:
                try:
                    data, addr = sock.recvfrom(10)
                    message_parts = data.decode().split(Message.SEPARATOR)
                    message_type, process_id = message_parts[0], message_parts[1]

                    if message_type == Message.REQUEST:
                        self.handle_request(addr, process_id)
                    elif message_type == Message.RELEASE:
                        self.handle_release(process_id)

                    if self.queue:
                        addr, process_id = self.queue[0]
                        grant_message = Message.create_message(Message.GRANT, process_id)
                        sock.sendto(grant_message.encode(), addr)
                except ConnectionResetError:
                    continue


    def interface(self):
        while True:
            print("Bem Vindo ao Sistema")
            print("1 - Imprimir a Fila de Processos")	
            print("2 - Imprimir o Contador de Processos")
            print("3 - Sair")	
            command = input("Informe o Comando: ")

            if command == "1":
                with self.lock:
                    print("Fila de Processos Atual:", self.queue)
            elif command == "2":
                with self.lock:
                    print("Contador de Processos:", self.process_counters)
            elif command == "3":
                print("Finalizando...")
                sys.exit(0)
                break

    def run(self):
        try:
            message_processing_thread = threading.Thread(target=self.process_messages)
            message_processing_thread.start()

            interface_thread = threading.Thread(target=self.interface)
            interface_thread.start()

            message_processing_thread.join()
            interface_thread.join()
        except KeyboardInterrupt:
            sys.exit(0)



if __name__ == "__main__":
    coordinator = Coordinator(5123)
    coordinator.run()

