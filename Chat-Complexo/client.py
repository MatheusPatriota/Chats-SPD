import socket
import threading
import sys

def authenticate(client_socket, client_username, client_password):
    client_socket.sendall(client_username.encode('utf-8'))
    client_socket.sendall(client_password.encode('utf-8'))
    auth_status = client_socket.recv(1024).decode('utf-8')
    if auth_status == "Autenticado":
        return True
    else:
        return False
    
def register(client_socket, client_username, client_password):
    client_socket.sendall(client_username.encode('utf-8'))
    client_socket.sendall(client_password.encode('utf-8'))
    reg_status = client_socket.recv(1024).decode('utf-8')
    if reg_status == "Cadastro realizado com sucesso":
        return True
    else:
        return False
    
def create_channel(client_socket):
    channel_name = input("Digite o nome do canal que deseja criar: ")
    client_socket.sendall(channel_name.encode('utf-8'))
    return channel_name

def join_channel(client_socket):
    channel_name = input("Digite o nome do canal que deseja participar: ")
    client_socket.sendall(channel_name.encode('utf-8'))
    return channel_name

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
        message = input()  # aguarda o usuário digitar uma mensagem
        client_socket.sendall(
            f"{client_name}:{message}".encode("utf-8")
        )  # envia a mensagem para o servidor juntamente com o nome do cliente

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))

while True:
    action = input("Digite 'register' para se cadastrar ou 'login' para entrar: ")
    if action in ["register", "login"]:
        client_socket.sendall(action.encode('utf-8'))
        break

client_username = input("Digite seu nome de usuário: ")
client_password = input("Digite sua senha: ")

if action == "register":
    if register(client_socket, client_username, client_password):
        print("Cadastro realizado com sucesso!")
    else:
        print("Falha no cadastro. Nome de usuário já existente.")
    client_socket.close()

elif action == "login":
    if authenticate(client_socket, client_username, client_password):
        client_name = input("Digite seu apelido: ")
        client_socket.sendall(client_name.encode('utf-8'))
        
        while True:
            channel_action = input("Digite 'create' para criar um canal ou 'join' para participar de um canal existente: ")
            if channel_action in ["create", "join"]:
                client_socket.sendall(channel_action.encode('utf-8'))
                break

        if channel_action == "create":
            channel_name = create_channel(client_socket)
            print(f"Canal '{channel_name}' criado e ingressado com sucesso!")
        elif channel_action == "join":
            channel_name = join_channel(client_socket)
            response = client_socket.recv(1024).decode('utf-8')
            if response == "fail":
                print("Falha ao ingressar no canal. Canal não encontrado.")
                client_socket.close()
                sys.exit()
            else:
                print(f"Ingressado com sucesso no canal '{channel_name}'")

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        send_thread = threading.Thread(target=send_messages, args=(client_socket, client_name))

        receive_thread.start()  # Inicia a thread para receber mensagens
        send_thread.start()     # Inicia a thread para enviar mensagens
    else:
        print("Falha na autenticação. Conexão encerrada.")
        client_socket.close()