def receive_decode(socket):  # process of receiving message buffer size, actual message and decoding it

    msg_length = socket.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = socket.recv(msg_length).decode(FORMAT)
        return msg


def send_encode(socket, msg):  # process of encoding message, getting it buffer size, sending buffer size and actual message

    msg = msg.encode(FORMAT)
    msg_length = len(msg)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))  #  add as many bytes as needed to the length to make it 64
    socket.send(send_length)
    socket.send(msg)


HEADER = 64
FORMAT = "utf8"
