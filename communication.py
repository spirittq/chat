def receive_decode(socket):

    msg_length = socket.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = socket.recv(msg_length).decode(FORMAT)
        return msg


def encode_send(socket, msg):

    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    socket.send(send_length)
    socket.send(message)


HEADER = 64
FORMAT = "utf8"