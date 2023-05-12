# Importa as bibliotecas necessárias
import socket
import threading
from random import randint
from message import Message
import time

# Função para enviar uma solicitação (request) ao servidor
def send_request():
    # Cria um socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Gera um ID de processo aleatório entre 1 e 1000
    process_id = randint(1, 1000)
    # Cria uma mensagem do tipo REQUEST com o ID do processo
    message = Message.create_message(Message.REQUEST, process_id)
    # Envia a mensagem para o servidor no endereço 'localhost' e porta 8888
    try:
        sock.sendto(message.encode(), ('localhost', 8888))
    except:
        print("Erro ao enviar mensagem")

    try:
        # Aguarda a resposta do servidor
        # recebe a resposta do servidor
        # caso exista alguem acessando a regiao critica, o servidor retorna a mensagem BUSY
        # caso contrario, o servidor retorna a mensagem GRANT
        # Fecha o socket
        print("Aguardando resposta do servidor...")
        data = sock.recv(1024)
        print(data.decode())
    except:
        print("Erro ao receber mensagem")
    
    data = data.decode()
    if(data == Message.GRANT):
        print("Servidor deu GRANT para o processo: ", process_id)
        time.sleep(0.5)
        # Cria uma mensagem do tipo RELEASE com o ID do processo
        message = Message.create_message(Message.RELEASE, process_id)
        # Envia a mensagem para o servidor no endereço 'localhost' e porta 8888
        try:
            sock.sendto(message.encode(), ('localhost', 8888))
        except:
            print("Erro ao enviar mensagem")

    
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
