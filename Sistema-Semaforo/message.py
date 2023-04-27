from config import MESSAGE_SIZE, SEPARATOR

def create_request_msg(process_id):
    return f"{SEPARATOR}REQUEST{SEPARATOR}{process_id}{SEPARATOR}".ljust(MESSAGE_SIZE, "0")

def create_grant_msg(process_id):
    return f"{SEPARATOR}GRANT{SEPARATOR}{process_id}{SEPARATOR}".ljust(MESSAGE_SIZE, "0")

def create_release_msg(process_id):
    return f"{SEPARATOR}RELEASE{SEPARATOR}{process_id}{SEPARATOR}".ljust(MESSAGE_SIZE, "0")

def parse_msg(msg):
    parts = msg.split(SEPARATOR)
    if len(parts) < 4:
        print(f"[ERROR] Mensagem inválida recebida: {msg}")
        return None, None

    msg_type = parts[1]
    try:
        process_id = int(parts[2])
    except ValueError:
        print(f"[ERROR] ID do processo inválido na mensagem: {msg}")
        return None, None

    return msg_type, process_id
