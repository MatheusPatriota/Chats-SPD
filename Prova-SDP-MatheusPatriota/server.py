import socket
import threading
import random

class User:
    def __init__(self, id, username, password, balance):
        self.id = id
        self.username = username
        self.password = password
        self.balance = balance
        self.transactions = []
        self.operations = []

users = [
    User(1, "user1", "pass1", 100),
    User(2, "user2", "pass2", 100),
    User(3, "user3", "pass3", 100),
]

authenticated_users = {}

def get_user(username, password):
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} conectado.")
    
    authenticated = False
    user = None
    
    while not authenticated:
        client_socket.send("Username: ".encode())
        username = client_socket.recv(1024).decode().strip()
        client_socket.send("Senha: ".encode())
        password = client_socket.recv(1024).decode().strip()
        
        user = get_user(username, password)
        if user:
            authenticated = True
            client_socket.send("AUTENTICADO".encode())
            authenticated_users[user.id] = user
            print(f"[AUTHENTICATION] Usuário {user.id} Autenticado.")
        else:
            client_socket.send("CREDENCIAIS INVÁLIDAS".encode())

    # envia informações de operação para o cliente
    message = "/----------------------------------/\n"
    message += "Bem vindo ao Matheus Bank!\n"
    message += "Digite o comando desejado:\n"
    message += "SALDO - Para ver o saldo da sua conta\n"
    message += "TRANSFERIR [ID-DESTINATÁRIO] [AMOUNT]: - Para transferir dinheiro para outra conta\n"
    message += "EXTRATO - Para imprimir o extrato das operações\n"
    message += "LOGOUT - Para sair do sistema\n"
    message += "/----------------------------------/\n"
    client_socket.send(message.encode())


    semaphore = threading.Semaphore()

    def request_critical_section():
        semaphore.acquire()
        print(f"[REQUEST] User {user.id} requested access to critical section.")
        client_socket.send("GRANTED".encode())
        print(f"[GRANT] Access granted to user {user.id}.")

    def release_critical_section():
        semaphore.release()
        print(f"[RELEASE] User {user.id} released critical section.")

    while True:
        msg = client_socket.recv(1024).decode().strip()
        
        if msg == "SALDO":
            request_critical_section()
            user.operations.append("OPERAÇÃO - SALDO - OK;")
            client_socket.send(f"Seu saldo atual é R${user.balance:.2f}".encode())
            client_socket.send(message.encode())
            release_critical_section()
        elif msg == "EXTRATO":
            request_critical_section()
            if not user.transactions:
                client_socket.send("Nenhuma transação encontrada.".encode())
            else:
                client_socket.send("\n".join(user.operations).encode())
            client_socket.send(message.encode())
            release_critical_section()
        elif msg.startswith("TRANSFERIR"):
            request_critical_section()
            dest_id, amount = map(int, msg.split()[1:])
            dest_user = authenticated_users.get(dest_id)
            if dest_user and user.balance >= amount:
                user.balance -= amount
                user.operations.append(f"OPERAÇÃO - TRANSFERÊNCIA - Transferência de R${amount:.2f} para o usuário {dest_id};")
                user.transactions.append(f"Transferência de R${amount:.2f} para o usuário {dest_id}")
                dest_user.balance += amount
                dest_user.transactions.append(f"Recebimento de R${amount:.2f} do usuário {user.id}")
                client_socket.send(f"Transferência de R${amount:.2f} para o usuário {dest_id} foi bem sucedida!".encode())
            else:
                client_socket.send("Transferência Falhou. Usuário Invalido ou Saldo Insuficiente.".encode())
            release_critical_section()

            client_socket.send(message.encode())
        elif msg == "LOGOUT":
            user.operations.append(f"OPERAÇÃO - LOGOUT - OK;")
            client_socket.send("Encerrando Conexão".encode())
            break
        else:
            client_socket.send("COMANDO INVÁLIDO".encode())
            client_socket.send(message.encode())

    client_socket.close()
    print(f"[DISCONNECT] {addr} Desconectado.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 12345))
    server.listen()

    print("[STARTING] Servidor está iniciando...")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
