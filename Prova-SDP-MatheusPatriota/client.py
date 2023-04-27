import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            print(msg)
        except:
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 12345))

    print("[CONNECTED] Connected to the server.")

    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        msg = input()
        if msg:
            client_socket.send(msg.encode())

        if msg == "LOGOUT":
            break

    client_socket.close()
    print("[DISCONNECTED] Disconnected from the server.")

if __name__ == "__main__":
    main()
