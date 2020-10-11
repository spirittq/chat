import socket
from threading import Thread


def accept_connection():
    while True:
        client_connection, client_address = SERVER.accept()
        addresses[client_connection] = client_address
        print(f"{client_address} has connected.")
        client_connection.send("Hello! Please enter your name.".encode(FORMAT))
        addresses[client_connection] = client_address
        Thread(target=handle_client, args=(client_connection, client_address)).start()


def handle_client(client, address):  # Takes client socket as argument.

    name = client.recv(BUFSIZ).decode(FORMAT)
    while name == "{is_typing}" or name == "{is_not_typing}" or name == "{seen}":
        if name == QUIT_MESSAGE:
            del clients[client]
            print(f"{address} has disconnected")
        else:
            name = client.recv(BUFSIZ).decode("utf8")
    if name != QUIT_MESSAGE:
        welcome = 'Welcome %s! If you ever want to quit, type {{{quit}}} to exit.' % name
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        broadcast1(bytes(msg, "utf8"))
        clients[client] = name

        while True:
            msg = client.recv(BUFSIZ)
            if msg == bytes("{is_typing}", "utf8"):
                broadcast1(bytes("%s is typing..." % name, "utf8"))
            elif msg == (bytes("{is_not_typing}", "utf8")):
                broadcast1(bytes("{is not typing}", "utf8"))
            elif msg == (bytes("{seen}", "utf8")):
                broadcast2(client, bytes("{seen}", "utf8"))
            elif msg != bytes("{{{quit}}}", "utf8"):
                broadcast2(client, msg, name + ": ")
            else:
                del clients[client]
                print(f"{address} has disconnected")
                broadcast2(bytes("%s has left the chat." % name, "utf8"))
                break


def broadcast1(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


def broadcast2(client, msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        if client == sock and msg != bytes("{seen}", "utf8"):
            sock.send(bytes(prefix, "utf8") + msg + bytes(" {received}", "utf8"))
        elif client == sock and msg == bytes("{seen}", "utf8"):
            pass
        else:
            sock.send(bytes(prefix, "utf8") + msg)


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
