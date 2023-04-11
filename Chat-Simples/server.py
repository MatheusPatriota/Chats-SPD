import socket
import threading

def handle_client(client_socket, client_address):
    print(f"Conexão estabelecida com {client_address}")
    client_name = client_socket.recv(1024).decode('utf-8') # recebe o nome do cliente
    while True:
        data = client_socket.recv(1024) # recebe dados do cliente
        if not data: # verifica se não há mais dados
            break
        try:
            sender_name, message = data.decode('utf-8').split(":") # separa o nome do remetente da mensagem
            print(f"{sender_name}: {message}") # exibe a mensagem na tela juntamente com o nome do remetente
            for client in clients: # envia a mensagem para todos os clientes conectados, exceto o remetente
                if client[0] != client_socket:
                    client[0].sendall(f"{sender_name}:{message}".encode('utf-8'))
        except ValueError:
            print(f"Mensagem inválida recebida de {client_address}: {data.decode('utf-8')}") # trata erros na mensagem recebida
    print(f"Conexão encerrada com {client_address}")
    client_socket.close() # encerra a conexão com o cliente
    clients.remove((client_socket, client_name)) # remove o cliente da lista de clientes conectados

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria um socket TCP/IP
server_socket.bind(('localhost', 8080)) # associa o socket a um endereço e porta
server_socket.listen(5) # aguarda conexões

clients = [] # lista de clientes conectados
while True:
    client_socket, client_address = server_socket.accept() # aguarda uma conexão
    clients.append((client_socket, client_address)) # adiciona o cliente à lista de clientes conectados
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address)) # cria uma thread para tratar o cliente
    thread.start() # inicia a thread
