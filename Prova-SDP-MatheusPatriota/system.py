import threading
import random
import time

F = 10
SEPARATOR = "|"

class Account:
    def __init__(self, id, balance):
        self.id = id
        self.balance = balance
        self.lock = threading.Lock()

class Operation:
    def __init__(self, op_type, src_account, dest_account, amount):
        self.op_type = op_type
        self.src_account = src_account
        self.dest_account = dest_account
        self.amount = amount

def generate_message(msg_id, process_id, op_type, amount):
    return f"{msg_id}{SEPARATOR}{process_id}{SEPARATOR}{op_type}{SEPARATOR}{amount:.2f}".ljust(F, "0")

def parse_message(message):
    msg_parts = message.split(SEPARATOR)
    return int(msg_parts[0]), int(msg_parts[1]), int(msg_parts[2]), float(msg_parts[3])

def process_request(account, operation_queue):
    while True:
        if operation_queue:
            op = operation_queue.pop(0)
            account.lock.acquire()
            if op.op_type == 1: # Request
                print(f"Request received from process {op.src_account} to account {op.dest_account}")
            elif op.op_type == 2: # Grant
                print(f"Grant received for account {op.dest_account}")
            elif op.op_type == 3: # Operation
                account.balance += op.amount
                print(f"Operation performed on account {op.dest_account}, new balance: {account.balance:.2f}")
            elif op.op_type == 4: # Release
                print(f"Release received for account {op.dest_account}")
                account.lock.release()

        time.sleep(1)

def main():
    accounts = [Account(i, 100) for i in range(5)]

    operation_queues = [[] for _ in accounts]

    for i, account in enumerate(accounts):
        threading.Thread(target=process_request, args=(account, operation_queues[i])).start()

    while True:
        src_account = random.choice(accounts)
        dest_account = random.choice(accounts)

        if src_account != dest_account and src_account.balance > 0:
            amount = random.uniform(1, src_account.balance)
            src_account.balance -= amount

            request_msg = generate_message(1, src_account.id, dest_account.id, 0)
            grant_msg = generate_message(2, src_account.id, dest_account.id, 0)
            operation_msg = generate_message(3, src_account.id, dest_account.id, amount)
            release_msg = generate_message(4, src_account.id, dest_account.id, 0)

            operation_queues[dest_account.id].append(Operation(*parse_message(request_msg)))
            operation_queues[dest_account.id].append(Operation(*parse_message(grant_msg)))
            operation_queues[dest_account.id].append(Operation(*parse_message(operation_msg)))
            operation_queues[dest_account.id].append(Operation(*parse_message(release_msg)))

        time.sleep(2)

if __name__ == "__main__":
    main()
