import socket
import threading


def authenticate(client_socket):
    username = client_socket.recv(1024).decode('utf-8')
    password = client_socket.recv(1024).decode('utf-8')
    if username in users and users[username] == password:
        client_socket.sendall("Autenticado".encode('utf-8'))
        return True
    else:
        client_socket.sendall("Falha na autenticação".encode('utf-8'))
        return False
    

def register(client_socket):
    username = client_socket.recv(1024).decode('utf-8')
    password = client_socket.recv(1024).decode('utf-8')
    if username not in users:
        users[username] = password
        client_socket.sendall("Cadastro realizado com sucesso".encode('utf-8'))
        return True
    else:
        client_socket.sendall("Nome de usuário já existente".encode('utf-8'))
        return False


def handle_client(client_socket, client_address, client_name, current_channel):
    print(f"Conexão estabelecida com {client_address} no canal '{current_channel}'")
    
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        try:
            sender_name, message = data.decode('utf-8').split(":")
            print(f"{sender_name}: {message}")
            for client in clients:
                if client[0] != client_socket and client[3] == current_channel:
                    client[0].sendall(f"{sender_name}:{message}".encode('utf-8'))
        except ValueError:
            print(f"Mensagem inválida recebida de {client_address}: {data.decode('utf-8')}")
    
    print(f"Conexão encerrada com {client_address}")
    client_socket.close()
    clients.remove((client_socket, client_address, client_name, current_channel))

def create_channel(client_socket):
    channel_name = client_socket.recv(1024).decode('utf-8')
    if channel_name not in channels:
        channels.append(channel_name)
        return channel_name
    return None

def join_channel(client_socket):
    channel_name = client_socket.recv(1024).decode('utf-8')
    if channel_name in channels:
        return channel_name
    return None

def client_auth_handler(client_socket, client_address):
    action = client_socket.recv(1024).decode('utf-8')

    if action == "register":
        if register(client_socket):
            client_socket.close()
        else:
            client_socket.close()
    elif action == "login":
        if authenticate(client_socket):
            client_name = client_socket.recv(1024).decode('utf-8')
            channel_action = client_socket.recv(1024).decode('utf-8')
            if channel_action == "create":
                channel_name = create_channel(client_socket)
            elif channel_action == "join":
                channel_name = join_channel(client_socket)

            if channel_name:
                clients.append((client_socket, client_address, client_name, channel_name))
                thread = threading.Thread(target=handle_client, args=(client_socket, client_address, client_name, channel_name))
                thread.start()
            else:
                client_socket.sendall("fail".encode('utf-8'))
                client_socket.close()
        else:
            client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8080))
server_socket.listen(5)

clients = []
channels = []
users = {"user1": "password1", "user2": "password2"}

while True:
    client_socket, client_address = server_socket.accept()
    auth_thread = threading.Thread(target=client_auth_handler, args=(client_socket, client_address))
    auth_thread.start()