import sys
from pathlib import Path
print(sys.path[0])
sys.path[0] = str(Path(sys.path[0]).parent.parent)
print(sys.path[0])



# https://pythonprogramming.net/python-3-tkinter-basics-tutorial/
import logging
import socket
import pickle
from tkinter import *

from tkinter import messagebox
from tkinter.ttk import Combobox


class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.init_window()
        self.makeConnnectionWithServer()

    # Creation of init_window
    def init_window(self):
        # changing the title of our master widget
        self.master.title("Login")

        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        Label(self, text="Naam:").grid(row=0)
        Label(self, text="Wachtwoord:", pady=10).grid(row=1)

        self.entry_naam = Entry(self, width=40)
        self.entry_wachtwoord = Entry(self, width=40, show="*")

        self.entry_naam.grid(row=0, column=1, sticky=E + W, padx=(5, 5), pady=(5, 5))
        self.entry_wachtwoord.grid(row=1, column=1, sticky=E + W, padx=(5, 5), pady=(5, 0))

        self.buttonCalculate = Button(self, text="Login", command=self.login)
        self.buttonCalculate.grid(row=3, column=0, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=N + S + E + W)

        Grid.rowconfigure(self, 3, weight=1)
        Grid.columnconfigure(self, 1, weight=1)

    def __del__(self):
        self.close_connection()

    def makeConnnectionWithServer(self):
        try:
            logging.info("Making connection with server...")
            # get local machine name
            host = socket.gethostname()
            port = 9999
            self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connection to hostname on the port.
            self.socket_to_server.connect((host, port))
            # NIEUW
            self.in_out_server = self.socket_to_server.makefile(mode='rwb')
            logging.info("Open connection with server succesfully")
        except Exception as ex:
            logging.error(f"Foutmelding: {ex}")
            messagebox.showinfo("Foutmelding", "Something has gone wrong...")


    def close_connection(self):
        try:
            logging.info("Close connection with server...")
            pickle.dump("CLOSE", self.in_out_server)
            self.in_out_server.flush()
            self.socket_to_server.close()
        except Exception as ex:
            logging.error("Foutmelding:close connection with server failed")

    def login(self):
        naam = self.entry_naam.get()
        wachtwoord = self.entry_wachtwoord.get()
        try:
            logging.info("Sending login data to server...")
            login_to_send = pickle.dumps(("LOGIN", (naam, wachtwoord)))
            pickle.dump(login_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Login data sent to server succesfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Commando received: {commando}")
            if commando == "OK":
                messagebox.showinfo("Login", "Login succesful")
            else:
                messagebox.showinfo("Login", "Login failed")
        except Exception as ex:
            logging.error(f"Foutmelding Client: {ex}")
            messagebox.showinfo("Foutmelding", "Something has gone wrong...")


logging.basicConfig(level=logging.INFO)

root = Tk()
# root.geometry("400x300")
app = Window(root)
root.mainloop()
