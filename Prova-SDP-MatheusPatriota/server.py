import socket
import threading
import datetime

def log_event(event):
    with open("log.txt", "a") as log_file:
        log_file.write(event + "\n")

class User:
    def __init__(self, id, username, chave, password, balance):
        self.id = id
        self.chave = chave
        self.username = username
        self.password = password
        self.balance = balance
        self.transactions = []
        self.operations = []


users = [
    User(1, "user1", "134", "pass1", 100),
    User(2, "user2", "122", "pass2", 100),
    User(3, "user3", "1114", "pass3", 100),
]

authenticated_users = {}


def get_user(username, password):
    for user in users:
        if user.username == username and user.password == password:
            return user
    return None


def handle_client(client_socket, addr):
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    print(f"[NEW CONNECTION] {addr} conectado. {timestamp}")
    log_event(f"[NEW CONNECTION] {addr} conectado. {timestamp}")

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
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[AUTHENTICATION] Usuário {user.id} Autenticado. - {timestamp}")
            log_event(f"[AUTHENTICATION] Usuário {user.id} Autenticado. - {timestamp}")
        else:
            client_socket.send("CREDENCIAIS INVÁLIDAS".encode())

    # envia informações de operação para o cliente
    message = "/----------------------------------/\n"
    message += "Bem vindo ao Matheus Bank!\n"
    message += "Digite o comando desejado:\n"
    message += "SALDO - Para ver o saldo da sua conta\n"
    message += "TRANSFERIR [ID-DESTINATÁRIO] [CHAVE] [AMOUNT]: - Para transferir dinheiro para outra conta\n"
    message += "EXTRATO - Para imprimir o extrato das operações\n"
    message += "LOGOUT - Para sair do sistema\n"
    message += "/----------------------------------/\n"
    client_socket.send(message.encode())

    semaphore = threading.Semaphore()

    def request_critical_section():
        semaphore.acquire()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(
            f"[REQUEST] User {user.id} requested access to critical section. {timestamp}")
        log_event(f"[REQUEST] User {user.id} requested access to critical section. {timestamp}")
        client_socket.send("GRANTED".encode())
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[GRANT] Access granted to user {user.id}. {timestamp}")
        log_event(f"[GRANT] Access granted to user {user.id}. {timestamp}")

    def release_critical_section():
        semaphore.release()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[RELEASE] User {user.id} released critical section. {timestamp}")
        log_event(f"[RELEASE] User {user.id} released critical section. {timestamp}")

    while True:
        msg = client_socket.recv(1024).decode().strip()

        if msg == "SALDO":
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            print(f"[OPERATION] User {user.id} consultou SALDO. {timestamp}")
            log_event(f"[OPERATION] User {user.id} consultou SALDO. {timestamp}")

            request_critical_section()
            user.operations.append("OPERAÇÃO - SALDO - OK;")
            client_socket.send(
                f"Seu saldo atual é R${user.balance:.2f}".encode())
            client_socket.send(message.encode())
            release_critical_section()
        elif msg == "EXTRATO":
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[OPERATION] User {user.id} consultou EXTRATO. {timestamp}")
            log_event(f"[OPERATION] User {user.id} consultou EXTRATO. {timestamp}")
            request_critical_section()
            if not user.transactions:
                client_socket.send("Nenhuma transação encontrada.".encode())
            else:
                client_socket.send("\n".join(user.operations).encode())
            client_socket.send(message.encode())
            release_critical_section()
        elif msg.startswith("TRANSFERIR"):
            request_critical_section()
            dest_id, dest_chave, amount = map(str, msg.split()[1:])
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[OPERATION] User {user.id} solicitou TRANSFERIR para o User { dest_id}. {timestamp}")
            log_event(f"[OPERATION] User {user.id} solicitou TRANSFERIR para o User { dest_id}. {timestamp}")
            dest_user = authenticated_users.get(int(dest_id))
            if dest_user and user.balance >= float(amount) and dest_user.chave == dest_chave:
                timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                user.balance -= float(amount)
                user.operations.append(
                    f"OPERAÇÃO - TRANSFERÊNCIA - Transferência de R${float(amount):.2f} para o usuário {dest_id};{timestamp}")
                user.transactions.append(
                    f"Transferência de R${float(amount):.2f} para o usuário {dest_id}")
                dest_user.balance += float(amount)
                dest_user.transactions.append(
                    f"Recebimento de R${float(amount):.2f} do usuário {user.id}")
                client_socket.send(
                    f"Transferência de R${float(amount):.2f} para o usuário {dest_id} foi bem sucedida!".encode())
            else:
                client_socket.send(
                    "Transferência Falhou. Usuário Invalido ou Saldo Insuficiente.".encode())
            release_critical_section()

            client_socket.send(message.encode())
        elif msg == "LOGOUT":
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"[OPERATION] User {user.id} solicitou LOGOUT. {timestamp}")
            log_event(f"[OPERATION] User {user.id} solicitou LOGOUT. {timestamp}")
            user.operations.append(f"OPERAÇÃO - LOGOUT - OK; {timestamp}")
            try:
                client_socket.send("Encerrando Conexão".encode())
            except ConnectionResetError:
                print(f"[CONNECTION] Conexão fechada pelo host remoto: {addr} - {timestamp}")
                log_event(f"[CONNECTION] Conexão fechada pelo host remoto: {addr} - {timestamp}")
                break
            break

        else:
            client_socket.send("COMANDO INVÁLIDO".encode())
            client_socket.send(message.encode())

    client_socket.close()
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[DISCONNECT] {addr} Desconectado. {timestamp}")
    log_event(f"[DISCONNECT] {addr} Desconectado. {timestamp}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 12345))
    server.listen()
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[STARTING] Servidor está iniciando... {timestamp}")
    log_event(f"[STARTING] Servidor está iniciando... {timestamp}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(
            target=handle_client, args=(client_socket, addr))
        thread.start()
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1} - {timestamp}")
        log_event(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1} - {timestamp}")


if __name__ == "__main__":
    main()
