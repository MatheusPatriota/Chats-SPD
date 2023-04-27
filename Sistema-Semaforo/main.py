from coordinator import Coordinator
from process import Process
import threading
import time

COORDINATOR_HOST = "127.0.0.1"
COORDINATOR_PORT = 1235

if __name__ == "__main__":
    coordinator = Coordinator(COORDINATOR_HOST, COORDINATOR_PORT)
    coordinator_thread = threading.Thread(target=coordinator.start)
    coordinator_thread.start()

    time.sleep(1)  # Dá tempo para o coordenador iniciar

    processes = [
        Process(1, COORDINATOR_HOST, COORDINATOR_PORT),
        Process(2, COORDINATOR_HOST, COORDINATOR_PORT),
        Process(3, COORDINATOR_HOST, COORDINATOR_PORT),
        # Adicione mais processos conforme necessário
    ]

    process_threads = []
    for p in processes:
        t = threading.Thread(target=p.run)
        process_threads.append(t)
        t.start()

    for t in process_threads:
        t.join()
