import socket
from threading import Thread
from communication import receive_decode, send_encode


def accept_connection():

    while True:
        client_connection, client_address = server.accept()
        print(f"{client_address} has connected.")
        msg = "Hello! Please enter your name."
        send_encode(client_connection, msg)
        handle_client_thread = Thread(target=handle_client, args=(client_connection, client_address))
        handle_client_thread.start()


def handle_client(client, address):  # Takes client socket as argument.

    name = receive_decode(client)

    while name == TYPING_MESSAGE or name == NOT_TYPING_MESSAGE or name == SEEN_MESSAGE:
        if name == QUIT_MESSAGE:
            del clients[client]
            print(f"{address} has disconnected.")
        else:
            name = receive_decode(client)

    if name != QUIT_MESSAGE:
        msg = f"You are known as {name}. Type {QUIT_MESSAGE} to exit."
        send_encode(client, msg)
        msg = f"{name} has entered chat."
        broadcast_all(msg)
        clients[client] = name

        while True:
            msg = receive_decode(client)

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
                print(f"{address} has disconnected")
                msg = f"{name} has left the chat."
                broadcast_all(msg)
                broadcast_all(NOT_TYPING_MESSAGE)
                break


def broadcast_all(msg):

    for sock in clients:
        send_encode(sock, msg)


def broadcast_different(client, msg, name):

    for sock in clients:
        if msg == SEEN_MESSAGE:
            if client == sock:
                pass
            else:
                send_encode(sock, SEEN_MESSAGE)
        else:
            if client == sock:
                send_encode(sock, "You: " + msg + " " + RECEIVED_MESSAGE)
            else:
                send_encode(sock, name + ": " + msg)


clients = {}

# HOST = socket.gethostbyname(socket.gethostname())
HOST = 'localhost'
PORT = 8080
ADDR = (HOST, PORT)

QUIT_MESSAGE = "{{{quit}}}"
TYPING_MESSAGE = "{{{typing}}}"
NOT_TYPING_MESSAGE = "{{{not_typing}}}"
SEEN_MESSAGE = "{{{seen}}}"
NAME_MESSAGE = "{{{name}}}"
SENT_MESSAGE = "{{{sent}}}"
RECEIVED_MESSAGE = "{{{received}}}"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

if __name__ == "__main__":
    server.listen(2)
    print(f"Server is listening on {HOST}")
    accept_connection_thread = Thread(target=accept_connection)
    accept_connection_thread.start()
    accept_connection_thread.join()
    server.close()
