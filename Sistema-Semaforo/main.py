import threading
from process import Process
from coordinator import Coordinator
import sys 

def run_process(process_id, coordinator_address):
    try:
        process = Process(process_id, coordinator_address)
        process.run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    coordinator_port = 5123
    coordinator_address = ("localhost", coordinator_port)

    # Inicie o coordenador
    coordinator = Coordinator(coordinator_port)
    coordinator_thread = threading.Thread(target=coordinator.run)
    coordinator_thread.start()

    # Inicie alguns processos
    num_processes = 5
    process_threads = []
    for i in range(num_processes):
        process_thread = threading.Thread(target=run_process, args=(str(i), coordinator_address))
        process_thread.start()
        process_threads.append(process_thread)
    
    try:
        coordinator_thread.join()
        for process_thread in process_threads:
            process_thread.join()
    except KeyboardInterrupt:
        sys.exit(0)

