# Importa as bibliotecas necessárias
import socket
import threading
import datetime
from message import Message
import time

# Função para registrar eventos no log.txt


def log_event(event):
    with open("log.txt", "a") as log_file:
        log_file.write(event + "\n")

# Classe Server


class Server:
    def __init__(self):
        self.mutex = threading.Lock()
        self.queue = []
        self.fila_processos = []
        self.processos_atendidos = []
        self.vezes_atendidos = {}
        self.processo_em_atendimento = None

        self.processes = {}
        self.running = True
        self.process_count = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('localhost', 8888))
        self.isGranted = False

    # Inicia o servidor
    def start(self):
        # Registra no log que o servidor está iniciando
        log_event(
            f"[STARTING] SERVIDOR SENDO INICIADO  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        # Cria a thread para receber mensagens
        self.thread_receive = threading.Thread(target=self.receive)
        self.thread_receive.start()

        # Cria a thread para a interface do usuário
        self.thread_interface = threading.Thread(target=self.interface)
        self.thread_interface.start()

    # Função que recebe mensagens dos processos
    def receive(self):
        while True:
            # if(not len(self.fila_processos) > 0):
            #     print("Acabaram os Processos!")
            #     break
            try:
                # Recebe os dados e o endereço do processo
                data, addr = self.socket.recvfrom(1024)

                # Extrai informações da mensagem
                message_type, process_id, _ = data.decode().split(Message.SEPARATOR)
                process_id = int(process_id)

                self.fila_processos.append(process_id)

                print("mensagem recebida: ", message_type, process_id)
                if message_type == Message.REQUEST:

                    print("Request recebido")
                    if (self.processo_em_atendimento == None):
                        print("Processo colocado em atendimento")
                        self.processo_em_atendimento = self.fila_processos.pop(0)
                        print("Processo atendimento", self.processo_em_atendimento)
                        grant_response = (
                            f"[GRANT] Mensagem enviada pelo coordenador dando acesso região critica. Acesso concedido ao processo:{process_id}.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                        print("grant", grant_response)
                        self.socket.sendto(
                            Message.GRANT.encode(),addr)
                    else:
                        wait_response = (
                            f"Outro Processo está ocupando a zona critica, aguarde....")
                        self.socket.sendto(
                            wait_response.encode(), addr)
                
                if message_type == Message.RELEASE:
                    print("Release recebido")
                    self.processo_em_atendimento = None
                    print("Processo em atendimento", self.processo_em_atendimento)
                    if (len(self.fila_processos) > 0):
                        print("Processo colocado em atendimento")
                        self.processo_em_atendimento = self.fila_processos.pop(0)
                        print("Processo atendimento", self.processo_em_atendimento)
                        grant_response = (
                            f"[GRANT] Mensagem enviada pelo coordenador dando acesso região critica. Acesso concedido ao processo:{process_id}.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                        print("grant", grant_response)
                        self.socket.sendto(
                            Message.GRANT.encode(),addr)
                    else:
                        print("Acabaram os Processos!")
                        break
                
                

                # # Verifica se o processo já está registrado e adiciona caso não esteja
                # if process_id not in self.processes:
                #     self.add_process(process_id, addr)
                # # Se a mensagem for do tipo REQUEST
                # if message_type == Message.REQUEST:
                #     # Adiciona o processo na fila
                #     self.queue.append(process_id)
                #     # Registra no log que o processo solicitou acesso à região crítica
                #     log_event(
                #         f"[REQUEST] Mensagem enviada pelo processo {process_id} para solicitar acesso região critica.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                #     # Se o acesso não foi concedido a nenhum processo
                #     if self.isGranted == False:
                #         # Atualiza o contador de vezes que o processo foi atendido
                #         if process_id in self.vezes_atendidos:
                #             self.vezes_atendidos[process_id] += 1
                #         else:
                #             self.vezes_atendidos[process_id] = 1

                #         # Concede o acesso à região crítica para o processo
                #         self.send_message(Message.GRANT, process_id)
                #         # Registra no log que o acesso foi concedido
                #         log_event(
                #             f"[GRANT] Mensagem enviada pelo coordenador dando acesso região critica. Acesso concedido ao processo:{process_id}.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                #         time.sleep(1)
                #         # Envia mensagem de RELEASE
                #         message = Message.create_message(
                #             Message.RELEASE, process_id)
                #         log_event(
                #             f"[RELEASE] Mensagem enviada pelo processo {process_id} ao sair da região critica.  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                #         log_event(f"Formato REQUEST - {message}")
                #         time.sleep(1)

                #         self.isGranted = False
                #     else:
                #         print("Aguardando processo sair da região critica...")
            except:
                print("NENHUM PROCESSO CONECTADO...")

    # Função para enviar mensagens aos processos
    def send_message(self, message_type, process_id):
        message = Message.create_message(message_type, process_id)
        self.socket.sendto(message.encode(), self.processes[process_id])

    # Função para adicionar um processo e seu endereço
    def add_process(self, process_id, addr):
        self.processes[process_id] = addr
        return process_id

    # Função para a interface do usuário
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
                    print(
                        f"Processo {process_id} foi atendido {self.vezes_atendidos[process_id]} vezes.")
                self.mutex.release()
            elif command == "3":
                self.running = False
                self.mutex.acquire()
                log_event(
                    f"[DESCONECTANDO] DESCONECTANDO DO SERVIDOR ....  {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                self.socket.close()
                self.mutex.release()
                break


# Inicializa e inicia o servidor
if __name__ == "__main__":
    server = Server()
    server.start()
