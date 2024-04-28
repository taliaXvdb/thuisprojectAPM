import sys
from pathlib import Path
import logging
import socket
from queue import Queue
from threading import Thread, enumerate
from tkinter import *
from tkinter import messagebox, ttk
import pandas as pd
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

        pages = [
            "Logs",
            "Popularity",
            "Online users",
            "Userbase",
            "Message"
        ]

        self.tabs = {}  # Initialize tabs dictionary here

        # Create tabs for each search
        for page in pages:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=page)
            self.tabs[page] = tab

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.show_results("Logs")


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

    def init_messages_queue(self):
        self.messages_queue = Queue()
        self.thread_listener_queue = Thread(target=self.print_messages_from_queue, name="Queue_listener_thread", daemon=True)
        self.thread_listener_queue.start()


    def print_messages_from_queue(self):
        message = self.messages_queue.get()
        while message != "CLOSE_SERVER":
            self.lstnumbers.insert(END, message + '\n')  # Insert the message into the Text widget
            self.messages_queue.task_done()
            message = self.messages_queue.get()


    def on_tab_changed(self, event):
        tab_id = event.widget.select()
        tab_name = event.widget.tab(tab_id, "text")
        print(tab_name)
        self.show_results(tab_name)

    def show_results(self, tab_name):
        if tab_name == "Logs":
            self.init_messages_queue()
            tab = self.tabs[tab_name]  # Get tab object
            self.lstnumbers = Text(tab, wrap=WORD)
            self.lstnumbers.pack(fill=Y, expand=True)

        elif tab_name == "Popularity":
            self.show_popularity()

        elif tab_name == "Online users":
            self.show_online_users()

        elif tab_name == "Userbase":
            self.show_userbase()

        elif tab_name == "Message":
            self.send_message()


    def show_popularity(self):
        usedbase = pd.read_csv("./Data/usedbase.csv")
        tab = self.tabs["Popularity"]
        self.tree = ttk.Treeview(tab)
        self.tree.pack(fill=BOTH, expand=1)
        self.tree["columns"] = ("Overview", "Prediction", "Sweetness", "Crunchiness")
        self.tree.column("#0", width=0, stretch=NO)
        self.tree.column("Overview", anchor=W, width=100)
        self.tree.column("Prediction", anchor=W, width=100)
        self.tree.column("Sweetness", anchor=W, width=100)
        self.tree.column("Crunchiness", anchor=W, width=100)
        self.tree.heading("#0", text="", anchor=W)
        self.tree.heading("Overview", text="Overview", anchor=W)
        self.tree.heading("Prediction", text="Prediction", anchor=W)
        self.tree.heading("Sweetness", text="Sweetness", anchor=W)
        self.tree.heading("Crunchiness", text="Crunchiness", anchor=W)

        for index, row in usedbase.iterrows():
            self.tree.insert("", index, text="Entry" + str(index), values=(row["Overview"], row["Prediction"], row["Sweetness"], row["Crunchiness"]))
        self.tree.pack()

    def show_online_users(self):
        pass

    def show_userbase(self):
        pass

    def send_message(self):
        pass
