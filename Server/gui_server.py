import sys
from pathlib import Path
import logging
import socket
from queue import Queue
from threading import Thread, enumerate
from tkinter import *
from tkinter import messagebox, ttk
import sys
from pathlib import Path
print(sys.path[0])                  #test
sys.path[0] = str(Path(sys.path[0]).parent)      #Hier aanpassen
print(sys.path[0])    
from server.server import ProjectServer

class ServerWindow(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.server = None
        self.thread_listener_queue=None
        self.init_messages_queue()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Server")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        self.top_bar = Frame(self)  # Frame for the top bar
        self.top_bar.pack(side=TOP, fill=X)

        self.title = Label(self.top_bar, text="Server Application")
        self.title.pack(side=LEFT, padx=(5, 5))

        self.btn_text = StringVar()
        self.btn_text.set("Start server")
        self.buttonServer = Button(self.top_bar, textvariable=self.btn_text, command=self.start_stop_server)
        self.buttonServer.pack(side=RIGHT, padx=(5, 5))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=1)


    def start_stop_server(self):
        if self.server is not None:
            self.__stop_server()
        else:
            self.__start_server()

    def __stop_server(self):
        self.server.stop_server()
        self.server = None
        logging.info("Server stopped")
        self.btn_text.set("Start server")

    def __start_server(self):
        self.server = ProjectServer(socket.gethostname(), 9999, self.messages_queue)
        self.server.init_server()
        self.server.start()  # in thread plaatsen!
        logging.info("Server started")
        self.btn_text.set("Stop server")
        self.show_tabs()

    def init_messages_queue(self):
        self.messages_queue = Queue()
        self.thread_listener_queue = Thread(target=self.print_messsages_from_queue, name="Queue_listener_thread", daemon=True)
        self.thread_listener_queue.start()

    def print_messsages_from_queue(self):
        message = self.messages_queue.get()
        while message != "CLOSE_SERVER":
            self.lstnumbers.insert(END, message)
            self.messages_queue.task_done()
            message = self.messages_queue.get()

    def show_tabs(self):
        self.tab1 = Frame(self.notebook)
        self.notebook.add(self.tab1, text="Logs")
        self.notebook.pack(fill=BOTH, expand=1)

        self.lstnumbers = Listbox(self.tab1)
        self.lstnumbers.pack(fill=BOTH, expand=1)

        self.tab2 = Frame(self.notebook)
        self.notebook.add(self.tab2, text="Popularity")
        self.notebook.pack(fill=BOTH, expand=1)

        self.tab3 = Frame(self.notebook)
        self.notebook.add(self.tab3, text="Online users")
        self.notebook.pack(fill=BOTH, expand=1)

        self.tab4 = Frame(self.notebook)
        self.notebook.add(self.tab4, text="Userbase")
        self.notebook.pack(fill=BOTH, expand=1)

        self.tab5 = Frame(self.notebook)
        self.notebook.add(self.tab5, text="Message")
        self.notebook.pack(fill=BOTH, expand=1)

        self.lstusers = Listbox(self.tab2)
        self.lstusers.pack(fill=BOTH, expand=1)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        tab_id = event.widget.select()
        tab_name = event.widget.tab(tab_id, "text")
        print(tab_name)

        if tab_name == "Logs":
            self.print_messsages_from_queue()

        elif tab_name == "Popularity":
            self.show_popularity()

        elif tab_name == "Online users":
            self.show_online_users()

        elif tab_name == "Userbase":
            self.show_userbase()

        elif tab_name == "Message":
            self.send_message()

    def show_popularity(self):
        pass

    def show_online_users(self):
        pass

    def show_userbase(self):
        pass

    def send_message(self):
        pass