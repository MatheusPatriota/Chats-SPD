import socket
import threading

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024) # recebe dados do servidor
        if not data: # verifica se não há mais dados
            break
        try:
            sender_name, message = data.decode('utf-8').split(":") # separa o nome do remetente da mensagem
            print(f"Mensagem recebida de {sender_name}: {message}") # exibe a mensagem na tela juntamente com o nome do remetente
        except ValueError:
            print(f"Mensagem inválida recebida do servidor: {data.decode('utf-8')}") # trata erros na mensagem recebida
    print("Conexão com o servidor encerrada")
    client_socket.close() # encerra a conexão com o servidor

def send_messages(client_socket, client_name):
    while True:
        print("Digite sua Mensagem: ")
        message = input() # aguarda o usuário digitar uma mensagem
        client_socket.sendall(f"{client_name}:{message}".encode('utf-8')) # envia a mensagem para o servidor juntamente com o nome do cliente

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria um socket TCP/IP
client_socket.connect(('localhost', 8080)) # conecta ao servidor

client_name = input("Digite seu nome de usuário: ") # solicita o nome do cliente
client_socket.sendall(client_name.encode('utf-8')) # envia o nome do cliente para o servidor

receive_thread = threading.Thread(target=receive_messages, args=(client_socket,)) # cria uma thread para receber mensagens
send_thread = threading.Thread(target=send_messages, args=(client_socket, client_name)) # cria uma thread para enviar mensagens

receive_thread.start() # inicia a thread de recebimento de mensagens
send_thread.start() # inicia a thread de envio de mensagens
