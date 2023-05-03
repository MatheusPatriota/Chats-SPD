import socket
import threading
from random import randint
from message import Message

def send_request():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    process_id = randint(1, 1000)  # Gerando um ID de processo aleatório entre 1 e 1000
    message = Message.create_message(Message.REQUEST, process_id)
    sock.sendto(message.encode(), ('localhost', 8888))
    sock.close()

def simulate_multiple_connections(num_processes):
    threads = []

    for _ in range(num_processes):
        thread = threading.Thread(target=send_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    num_processes = 5  # número de processos a serem simulados
    simulate_multiple_connections(num_processes)
