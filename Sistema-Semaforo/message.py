class Message:
    REQUEST = "REQUEST"
    GRANT = "GRANT"
    RELEASE = "RELEASE"
    SEPARATOR = "|"

    @staticmethod
    def create_message(message_type, process_id):
        return f"{message_type}{Message.SEPARATOR}{process_id}{Message.SEPARATOR}".ljust(10, "0")
