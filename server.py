import socket
from threading import Thread
from communication import receive_decode, encode_send


def accept_connection():
    while True:
        client_connection, client_address = SERVER.accept()
        addresses[client_connection] = client_address
        print(f"{client_address} has connected.")
        # client_connection.send("Hello! Please enter your name.".encode(FORMAT))
        encode_send(client_connection, "Hello! Please enter your name.")
        addresses[client_connection] = client_address
        Thread(target=handle_client, args=(client_connection, client_address)).start()


def handle_client(client, address):  # Takes client socket as argument.

    # name = client.recv(BUFSIZ).decode(FORMAT)
    name = receive_decode(client)
    while name == TYPING_MESSAGE or name == NOT_TYPING_MESSAGE or name == SEEN_MESSAGE:
        if name == QUIT_MESSAGE:
            del clients[client]
            print(f"{address} has disconnected.")
        else:
            # name = client.recv(BUFSIZ).decode("utf8")
            name = receive_decode(client)
    if name != QUIT_MESSAGE:
        welcome = 'Welcome %s! If you ever want to quit, type {{{quit}}} to exit.' % name
        # client.send(bytes(welcome, "utf8"))
        encode_send(client, welcome)
        msg = "%s has joined the chat!" % name
        broadcast_all(msg)
        clients[client] = name

        while True:
            # msg = client.recv(BUFSIZ)
            # if msg == bytes("{is_typing}", "utf8"):
            #     broadcast1(bytes("%s is typing..." % name, "utf8"))
            # elif msg == (bytes("{is_not_typing}", "utf8")):
            #     broadcast1(bytes("{is not typing}", "utf8"))
            # elif msg == (bytes("{seen}", "utf8")):
            #     broadcast2(client, bytes("{seen}", "utf8"))
            # elif msg != bytes("{{{quit}}}", "utf8"):
            #     broadcast2(client, msg, name + ": ")
            # else:
            #     del clients[client]
            #     print(f"{address} has disconnected")
            #     broadcast2(bytes(client, "%s has left the chat." % name, "utf8"))
            #     break
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
                broadcast_different(client, f"{name} has left the chat.", name)
                break


def broadcast_all(msg):
    """Broadcasts a message to all the clients."""

    for sock in clients:
        # sock.send(bytes(prefix, "utf8") + msg)
        encode_send(sock, msg)


def broadcast_different(client, msg, name):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        # if client == sock and msg != SEEN_MESSAGE:
        #     # sock.send(bytes(prefix, "utf8") + msg + bytes(" {received}", "utf8"))
        #     encode_send(sock, "You: " + msg + RECEIVED_MESSAGE)
        # elif client == sock and msg == SEEN_MESSAGE:
        #     pass
        # else:
        #     # sock.send(bytes(prefix, "utf8") + msg)
        #     encode_send(sock, name + ": " + msg)
        if msg == SEEN_MESSAGE:
            if client == sock:
                pass
            else:
                encode_send(sock, SEEN_MESSAGE)
        else:
            if client == sock:
                encode_send(sock, "You: " + msg + " " + RECEIVED_MESSAGE)
            else:
                encode_send(sock, name + ": " + msg)


clients = {}
addresses = {}

HEADER = 64
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8080
ADDR = (HOST, PORT)
FORMAT = "utf8"
QUIT_MESSAGE = "{{{quit}}}"
TYPING_MESSAGE = "{{{typing}}}"
NOT_TYPING_MESSAGE = "{{{not_typing}}}"
SEEN_MESSAGE = "{{{seen}}}"
NAME_MESSAGE = "{{{name}}}"
SENT_MESSAGE = "{{{sent}}}"
RECEIVED_MESSAGE = "{{{received}}}"

BUFSIZ = 1024

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(2)
    print(f"Server is listening on {HOST}")
    thread = Thread(target=accept_connection)
    thread.start()
    thread.join()
    SERVER.close()
