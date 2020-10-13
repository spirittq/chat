import socket
from threading import Thread
from communication import receive_decode, send_encode
import logging

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def accept_connection():
    try:
        while True:
            client_connection, client_address = server.accept()
            logging.info(f"{client_address} has connected.")
            msg = "Hello! Please enter your name."
            send_encode(client_connection, msg)  # sends the first message to the client
            handle_client_thread = Thread(target=handle_client, args=(client_connection, client_address))
            handle_client_thread.start()
    except Exception:
        logging.exception("accept connection")


def handle_client(client, address):
    try:
        name = getting_name(client, address)  # first received message is the name

        if name != QUIT_MESSAGE:
            name = setting_name(name, client)
            processing_msg(name, client, address)

    except Exception:
        logging.exception("handle client")


def getting_name(client, address):
    try:
        while True:
            name = receive_decode(client)  # avoid name accidentally be set as system message
            if name == TYPING_MESSAGE or name == NOT_TYPING_MESSAGE or name == SEEN_MESSAGE:
                pass
            elif name == QUIT_MESSAGE:
                logging.info(f"{address} has disconnected.")
                return name
            else:
                return name
    except Exception:
        logging.exception("getting_name")


def setting_name(name, client):
    try:
        name = name.replace(CHECK_MESSAGE, '')
        msg = f"You are known as {name}. Type {QUIT_MESSAGE} to exit."
        send_encode(client, msg)
        msg = f"{name} has entered chat."
        broadcast_all(msg)
        clients[client] = name  # clients is used later in broadcasting
        return name
    except Exception:
        logging.exception('setting_name')


def processing_msg(name, client, address):
    try:
        while True:
            msg = receive_decode(client)  # check if system message or user message is received

            if msg == TYPING_MESSAGE:
                broadcast_all(name + " is " + TYPING_MESSAGE)
            elif msg == NOT_TYPING_MESSAGE:
                broadcast_all(NOT_TYPING_MESSAGE)
            elif msg == SEEN_MESSAGE:
                broadcast_different(client, SEEN_MESSAGE, name)
            elif msg != QUIT_MESSAGE:
                broadcast_different(client, msg, name)
            else:
                del clients[client]
                logging.info(f"{address} has disconnected")
                msg = f"{name} has left the chat."
                broadcast_all(msg)
                broadcast_all(NOT_TYPING_MESSAGE)
                break
    except Exception:
        logging.exception("processing_msg")


def broadcast_all(msg):  # same message is sent to all clients
    try:
        for sock in clients:
            send_encode(sock, msg)
    except Exception:
        logging.exception("broadcast_all")


def broadcast_different(client, msg, name):  # different message is sent to client-sender and client-receiver
    try:
        for sock in clients:
            if msg == SEEN_MESSAGE:
                if client == sock:
                    pass
                else:
                    send_encode(sock, SEEN_MESSAGE)
            else:
                if client == sock:
                    send_encode(sock, RECEIVED_MESSAGE)
                else:
                    send_encode(sock, name + ": " + msg.replace(CHECK_MESSAGE, ""))
    except Exception:
        logging.exception("broadcast_different")


try:
    logging.info("Starting Server")

    clients = {}

    # HOST = socket.gethostbyname(socket.gethostname())
    HOST = 'localhost'
    PORT = 8080
    ADDR = (HOST, PORT)

    # system messages used to differentiate what each received message does
    QUIT_MESSAGE = "{{{quit}}}"
    TYPING_MESSAGE = "{{{typing}}}"
    NOT_TYPING_MESSAGE = "{{{not_typing}}}"
    SEEN_MESSAGE = "{{{seen}}}"
    SENT_MESSAGE = "{{{sent}}}"
    RECEIVED_MESSAGE = "{{{received}}}"
    CHECK_MESSAGE = "{{{safeguard}}}"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
except Exception:
    logging.exception("Error in initializing.")

if __name__ == "__main__":
    try:
        server.listen(2)
        logging.info(f"Server is listening on {HOST}")
        accept_connection_thread = Thread(target=accept_connection)
        accept_connection_thread.start()
        accept_connection_thread.join()
        server.close()
    except Exception:
        logging.exception("An error occured.")
        server.close()