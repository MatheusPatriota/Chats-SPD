import socket
import threading
import datetime
from message import Message
import time


def log_event(event):
    with open("log.txt", "a") as log_file:
        log_file.write(event + "\n")


class Server:
    def __init__(self):
        self.mutex = threading.Lock()
        self.queue = []
        self.processes = {}
        self.running = True
        self.process_count = 0
        self.vezes_atendidos = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', 8888))
        self.isGranted = False

    def start(self):
        log_event(
            f"[STARTING] SERVIDOR SENDO INICIADO  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.thread_receive = threading.Thread(target=self.receive)
        self.thread_receive.start()

        self.thread_interface = threading.Thread(target=self.interface)
        self.thread_interface.start()

    def receive(self):
        while self.running:
            try:
              data, addr = self.socket.recvfrom(1024)

              message_type, process_id, _ = data.decode().split(Message.SEPARATOR)
              process_id = int(process_id)

              if process_id not in self.processes:
                  self.add_process(process_id, addr)
              if message_type == Message.REQUEST:
                  self.queue.append(process_id)
                  log_event(
                      f"[REQUEST] Mensagem enviada pelo processo {process_id} para solicitar acesso região critica.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                  if self.isGranted == False:
                      if process_id in self.vezes_atendidos:
                          self.vezes_atendidos[process_id] += 1
                      else:
                          self.vezes_atendidos[process_id] = 1

                          
                      self.send_message(Message.GRANT, process_id)
                      log_event(
                          f"[GRANT] Mensagem enviada pelo coordenador dando acesso região critica. Acesso concedido ao processo:{process_id}.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                      time.sleep(1)
                      message = Message.create_message(Message.RELEASE, process_id)
                      log_event(
                      f"[RELEASE] Mensagem enviada pelo processo {process_id} ao sair da região critica.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                      log_event(
                          f"Formato REQUEST - {message}")
                      time.sleep(1)

                      self.isGranted = False
                  else:
                      print("Aguardando processo sair da região critica...")
            except:
                print("NENHUM PROCESSO CONECTADO...")
            

    def send_message(self, message_type, process_id):
        message = Message.create_message(message_type, process_id)
        self.socket.sendto(message.encode(), self.processes[process_id])

    def add_process(self, process_id, addr):
        self.processes[process_id] = addr
        return process_id

    def interface(self):
        while True:
            print("Bem vindo ao servidor!")
            print("1 - Ver fila")
            print("2 - Ver quantas vezes cada processo foi atendido")
            print("3 - Desconectar")
            command = input("Digite um comando: ")

            if command == "1":
                self.mutex.acquire()
                print(self.queue)
                self.mutex.release()
            elif command == "2":
                self.mutex.acquire()
                for process_id in self.vezes_atendidos:
                  print(f"Processo {process_id} foi atendido {self.vezes_atendidos[process_id]} vezes.")
               
                    
                self.mutex.release()
            elif command == "3":
                self.running = False
                self.mutex.acquire()
                log_event(
                    f"[DESCONECTANDO] DESCONECTANDO DO SERVIDOR ....  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                self.socket.close()
                self.mutex.release()
                break


if __name__ == "__main__":
    server = Server()
    server.start()
