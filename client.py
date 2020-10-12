import socket
from threading import Thread
from threading import Timer
import tkinter
from communication import receive_decode, send_encode
import logging

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')


def receive():
    try:
        while True:
            try:
                msg = receive_decode(client_socket)
                if msg[-12:] == TYPING_MESSAGE:
                    gui_typing_indicator.config(text=msg)
                elif msg == NOT_TYPING_MESSAGE:
                    gui_typing_indicator.config(text='')
                elif msg == SEEN_MESSAGE and msg == gui_msg_list.get("end"):
                    pass
                else:
                    if gui_msg_list.get("end") == SEEN_MESSAGE or gui_msg_list.get("end") == SENT_MESSAGE or gui_msg_list.get("end") == RECEIVED_MESSAGE:
                        gui_msg_list.delete("end")
                    gui_msg_list.insert("end", msg)
            except OSError:
                break
    except Exception:
        logging.exception("receive")


def send(event=None):
    try:
        msg = gui_msg_input.get()

        if msg != "":
            if msg != QUIT_MESSAGE:
                if gui_msg_list.get("end") != "Hello! Please enter your name.":
                    if gui_msg_list.get("end") == SEEN_MESSAGE or gui_msg_list.get("end") == SENT_MESSAGE or gui_msg_list.get("end") == RECEIVED_MESSAGE:
                        gui_msg_list.delete("end")
                    gui_msg_list.insert("end", "You: " + msg)
                    gui_msg_list.insert("end", SENT_MESSAGE)
                    gui_msg_input.set("")
                    send_encode(client_socket, msg + CHECK_MESSAGE)
                    not_typing()
                else:
                    gui_msg_input.set("")
                    send_encode(client_socket, msg + CHECK_MESSAGE)
                    not_typing()
            else:
                gui_msg_list.insert("end", QUIT_MESSAGE)
                send_encode(client_socket, QUIT_MESSAGE)
                not_typing()
                timer.cancel()
                client_socket.close()
                gui.quit()
    except Exception:
        logging.exception("send")


def on_closing(event=None):

    try:
        gui_msg_input.set(QUIT_MESSAGE)
        timer.cancel()
        send_encode(client_socket, QUIT_MESSAGE)
        send()
    except Exception:
        logging.exception("on_closing")


def typing(event=None):

    try:
        msg = gui_msg_input.get()
        timer.cancel()

        if msg != "":
            send_encode(client_socket, TYPING_MESSAGE)
            new_timer()
            timer.start()
        else:
            not_typing()
    except Exception:
        logging.exception("typing")


def not_typing():

    try:
        send_encode(client_socket, NOT_TYPING_MESSAGE)
    except Exception:
        logging.exception("not_typing")


def new_timer():

    try:
        global timer
        timer = Timer(3, not_typing)
    except Exception:
        logging.exception("new_timer")


def print_script():
    try:
        with open(f"{gui.title()}_transcript.txt", 'w') as file:
            get_transcript = gui_msg_list.get(0, "end")
            for msg in get_transcript:
                file.write(msg + '\n')
    except Exception:
        logging.exception("print_script")


def seen(event=None):

    try:
        if gui_msg_list.get("end") != SEEN_MESSAGE:
            send_encode(client_socket, SEEN_MESSAGE)
    except Exception:
        logging.exception("seen")


try:
    gui = tkinter.Tk()
    gui.title("Your chat")
    gui_msg_frame = tkinter.Frame(gui)
    gui_msg_input = tkinter.StringVar()
    gui_msg_frame_scrollbar = tkinter.Scrollbar(gui_msg_frame)
    gui_msg_list = tkinter.Listbox(gui_msg_frame, height=15, width=50, yscrollcommand=gui_msg_frame_scrollbar.set)
    gui_typing_indicator = tkinter.Label(gui, width=50)
    gui_entry_field = tkinter.Entry(gui, textvariable=gui_msg_input)
    gui_entry_field.bind('<KeyRelease>', typing)
    gui_entry_field.bind("<Return>", send)
    gui.bind("<FocusIn>", seen)
    gui_send_button = tkinter.Button(gui, text="Send", command=send)
    gui_print_button = tkinter.Button(gui, text="Print", command=print_script)

    gui_msg_frame_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    gui_msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    gui_msg_frame.pack()
    gui_entry_field.pack()
    gui_send_button.pack()
    gui_print_button.pack()
    gui_typing_indicator.pack()
    gui.protocol("WM_DELETE_WINDOW", on_closing)
except Exception:
    logging.exception("Error in GUI")

try:
    new_timer()
except Exception:
    logging.exception("Error with timer")

try:
    HOST = 'localhost'
    PORT = 8080

    QUIT_MESSAGE = "{{{quit}}}"
    TYPING_MESSAGE = "{{{typing}}}"
    NOT_TYPING_MESSAGE = "{{{not_typing}}}"
    SEEN_MESSAGE = "{{{seen}}}"
    SENT_MESSAGE = "{{{sent}}}"
    RECEIVED_MESSAGE = "{{{received}}}"
    CHECK_MESSAGE = "{{{safeguard}}}"

    ADDR = (HOST, PORT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)

    receive_thread = Thread(target=receive)
    receive_thread.start()
    tkinter.mainloop()
except Exception:
    logging.exception("Error in initializing and connecting")
