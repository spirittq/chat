from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from threading import Timer
import tkinter


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg[-13:] == " is typing...":
                typing_label.config(text=msg)
            elif msg == "{is not typing}":
                typing_label.config(text='')
            elif msg == "{seen}" and msg != msg_list.get("end"):
                msg_list.insert(tkinter.END, msg)
            elif msg == "{seen}" and msg == msg_list.get("end"):
                pass
            else:
                if msg_list.get("end") == "{seen}" or msg_list.get("end")[-6:] == "{Sent}":
                    print("before delete: " + msg_list.get("end"))
                    msg_list.delete("end")
                    print("after delete: " + msg_list.get("end"))
                msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    if msg_list.get("end") == "{seen}":
        msg_list.delete("end")
    msg_list.insert(tkinter.END, msg + "{Sent}")
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes("{is_not_typing}", "utf8"))
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        t.cancel()
        client_socket.close()
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    t.cancel()
    client_socket.send(bytes("{quit}", "utf8"))
    send()


def typing(event=None):
    msg = my_msg.get()
    t.cancel()
    if msg != '':
        client_socket.send(bytes("{is_typing}", "utf8"))
        newTimer()
        t.start()
    else:
        client_socket.send(bytes("{is_not_typing}", "utf8"))


def not_typing():
    client_socket.send(bytes("{is_not_typing}", "utf8"))


def newTimer():
    global t
    t = Timer(5, not_typing)


newTimer()


def print_script():
    with open("transcript.txt", 'w') as file:
        get_transcript = msg_list.get(0, tkinter.END)
        print(get_transcript)
        for msg in get_transcript:
            file.write(msg + '\n')


def seen(event=None):
    if msg_list.get("end") != "{seen}":
        client_socket.send(bytes("{seen}", "utf8"))


top = tkinter.Tk()
top.title("Chatter")
messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
typing_label = tkinter.Label(top, width=50)

scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind('<KeyRelease>', typing)
entry_field.bind("<Return>", send)
top.bind("<FocusIn>", seen)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
print_button = tkinter.Button(top, text="Print", command=print_script)
send_button.pack()
print_button.pack()
typing_label.pack()
top.protocol("WM_DELETE_WINDOW", on_closing)

# HOST = input('Enter host: ')
HOST = '127.0.0.1'
# PORT = input('Enter port: ')
PORT = '33000'
if not PORT:
    PORT = 33000  # Default value.
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.