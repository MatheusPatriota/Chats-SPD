import socket
import time
import random
from message import Message
import sys
class Process:
    def __init__(self, process_id, coordinator_address):
        self.process_id = process_id
        self.coordinator_address = coordinator_address

    def request_critical_region(self):
        message = Message.create_message(Message.REQUEST, self.process_id)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), self.coordinator_address)

    def release_critical_region(self):
        message = Message.create_message(Message.RELEASE, self.process_id)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(message.encode(), self.coordinator_address)

    def run(self):
        try:
            while True:
                self.request_critical_region()
                time.sleep(random.uniform(1, 5))
                self.release_critical_region()
                time.sleep(random.uniform(1, 5))
        except KeyboardInterrupt:
            sys.exit(0)
