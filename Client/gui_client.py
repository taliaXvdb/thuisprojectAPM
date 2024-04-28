import logging
import socket
import pickle
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk
import pandas as pd


class Window(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.init_window()
        self.make_connection_with_server()
        self.current_user = None

    def init_window(self):
        self.master.title("Login")
        self.pack(fill=tk.BOTH, expand=1)

        tk.Label(self, text="Username:").grid(row=0)
        tk.Label(self, text="Password:", pady=10).grid(row=1)

        self.entry_username = tk.Entry(self, width=40)
        self.entry_password = tk.Entry(self, width=40, show="*")

        self.entry_username.grid(row=0, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 5))
        self.entry_password.grid(row=1, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 0))

        self.button_login = tk.Button(self, text="Login", command=self.login)
        self.button_login.grid(row=3, column=0, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        self.button_register = tk.Button(self, text="Register", command=self.register)
        self.button_register.grid(row=4, column=0, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(self, 3, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

    def __del__(self):
        self.close_connection()

    def make_connection_with_server(self):
        try:
            logging.info("Making connection with server...")
            host = socket.gethostname()
            port = 9999
            self.socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_to_server.connect((host, port))
            self.in_out_server = self.socket_to_server.makefile(mode='rwb')
            logging.info("Open connection with server successfully")
        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def close_connection(self):
        try:
            logging.info("Closing connection with server...")
            pickle.dump("CLOSE", self.in_out_server)
            self.in_out_server.flush()
            self.socket_to_server.close()
        except Exception as ex:
            logging.error("Error: Failed to close connection with server")

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        try:
            logging.info("Sending login data to server...")
            login_to_send = pickle.dumps(("LOGIN", (username, password)))
            pickle.dump(login_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Login data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")

            if commando == "OK":
                result = messagebox.showinfo("Login", "Login successful")
                if result == "ok":
                    self.current_user = username
                    self.show_main_window()
            else:
                messagebox.showinfo("Login", "Login failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def register(self):
        for widget in self.winfo_children():
            logging.info("Close current window")
            widget.destroy()
        
        self.master.title("Register")
        self.pack(fill=tk.BOTH, expand=1)

        tk.Label(self, text="Username:").grid(row=0)
        tk.Label(self, text="Password:", pady=10).grid(row=1)

        self.entry_username = tk.Entry(self, width=40)
        self.entry_password = tk.Entry(self, width=40, show="*")

        self.entry_username.grid(row=0, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 5))
        self.entry_password.grid(row=1, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 0))

        self.button_register = tk.Button(self, text="Register", command=self.register_user)
        self.button_register.grid(row=3, column=0, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(self, 3, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)

    def register_user(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        try:
            logging.info("Sending register data to server...")
            register_to_send = pickle.dumps(("REGISTER", (username, password)))
            pickle.dump(register_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Register data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")

            if commando == "OK":
                result = messagebox.showinfo("Register", "Register successful")
                if result == "ok":
                    self.show_main_window()
            else:
                messagebox.showinfo("Register", "Register failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_main_window(self):
        logging.info("Close current window")
        for widget in self.winfo_children():
            widget.destroy()
        
        self.master.title("Main")
        self.pack(fill=tk.BOTH, expand=1)

        self.top_bar = tk.Frame(self)  # Frame for the top bar
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        self.label_user = tk.Label(self.top_bar, text=f"Welcome: {self.current_user}")
        self.label_user.pack(side=tk.LEFT, padx=(5, 5))

        self.button_logout = tk.Button(self.top_bar, text="Logout", command=self.logout)
        self.button_logout.pack(side=tk.RIGHT, padx=(5, 5))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=1)


        # Define a list of all possible searches
        searches = [
            "Overview",
            "Prediction",
            "Sweetness",
            "Crunchiness",
        ]

        # Create tabs for each search
        for search in searches:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=search)

        # Bind the tab changed event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.show_search_result("Overview")
        

    def on_tab_changed(self, event):
        try:
            selected_tab_index = event.widget.index("current")
            selected_tab_text = event.widget.tab(selected_tab_index, "text")
            logging.info(f"Selected tab: {selected_tab_text}")
            search_to_send = pickle.dumps(("SEARCH", selected_tab_text))
            pickle.dump(search_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Search data sent to server successfully")
            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")
            if commando == "OK":
                logging.info("Search successful")
                self.show_search_result(selected_tab_text)
            else:
                messagebox.showinfo("Search", "Search failed")
        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_search_result(self, search):
        if search == "Overview":
            existing_tab = None
            for tab_id in self.notebook.tabs():
                if self.notebook.tab(tab_id, "text") == search:
                    existing_tab = self.notebook.nametowidget(tab_id)
                    break

            if existing_tab:
                self.notebook.select(existing_tab)
                if existing_tab.winfo_children():
                    self.clear_image(existing_tab)
                self.show_image(self.notebook.nametowidget(existing_tab))

            else:
                tab = ttk.Frame(self.notebook, padding=2)
                self.notebook.add(tab, text=search)
                self.show_image(tab)

    def clear_image(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()


    def show_image(self, parent):
        img = Image.open("../size_plot.png")
        img = img.resize((1200, 800))
        img = ImageTk.PhotoImage(img)

        label = tk.Label(parent, image=img)
        label.image = img
        label.pack()


    def logout(self):
        self.close_connection()
        self.master.destroy()


logging.basicConfig(level=logging.INFO)

root = tk.Tk()
app = Window(root)
root.mainloop()