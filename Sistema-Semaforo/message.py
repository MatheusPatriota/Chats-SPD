class Message:
    SEPARATOR = "|"
    F = 10

    REQUEST = "1"
    GRANT = "2"
    RELEASE = "3"

    @staticmethod
    def create_message(message_type, process_id):
        message = f"{message_type}{Message.SEPARATOR}{process_id}{Message.SEPARATOR}"
        padding = "0" * (Message.F - len(message))
        return message + padding
