from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings from the cave!" +
                          "Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""
    name = client.recv(BUFSIZ).decode("utf8")
    while name == "{is_typing}" or name == "{is_not_typing}" or name == "{seen}":
        name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
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
        elif msg != bytes("{quit}", "utf8"):
            broadcast2(client, msg, name + ": ")
        else:
            del clients[client]
            broadcast1(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast1(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf8") + msg)


def broadcast2(client, msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    for sock in clients:
        if client == sock and msg != bytes("{seen}", "utf8"):
            sock.send(bytes(prefix, "utf8") + msg + bytes(" {Received}", "utf8"))
        elif client == sock and msg == bytes("{seen}", "utf8"):
            pass
        else:
            sock.send(bytes(prefix, "utf8") + msg)


clients = {}
addresses = {}
HOST = ''
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(2)  # Listens for 2 connections at max.
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()  # Starts the infinite loop.
    ACCEPT_THREAD.join()
    SERVER.close()
