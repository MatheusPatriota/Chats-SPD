# Importa as bibliotecas necessárias
import socket
import threading
from random import randint
from message import Message

# Função para enviar uma solicitação (request) ao servidor
def send_request():
    # Cria um socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Gera um ID de processo aleatório entre 1 e 1000
    process_id = randint(1, 1000)
    # Cria uma mensagem do tipo REQUEST com o ID do processo
    message = Message.create_message(Message.REQUEST, process_id)
    # Envia a mensagem para o servidor no endereço 'localhost' e porta 8888
    sock.sendto(message.encode(), ('localhost', 8888))
    # Fecha o socket
    sock.close()

# Função para simular várias conexões de processos
def simulate_multiple_connections(num_processes):
    # Lista para armazenar as threads
    threads = []

    # Cria e inicia 'num_processes' threads que enviam solicitações ao servidor
    for _ in range(num_processes):
        thread = threading.Thread(target=send_request)
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads serem finalizadas
    for thread in threads:
        thread.join()

# Ponto de entrada do script
if __name__ == "__main__":
    # Define o número de processos a serem simulados
    num_processes = 5
    # Chama a função para simular múltiplas conexões
    simulate_multiple_connections(num_processes)
