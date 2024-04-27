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

        tk.Label(self, text="Naam:").grid(row=0)
        tk.Label(self, text="Wachtwoord:", pady=10).grid(row=1)

        self.entry_naam = tk.Entry(self, width=40)
        self.entry_wachtwoord = tk.Entry(self, width=40, show="*")

        self.entry_naam.grid(row=0, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 5))
        self.entry_wachtwoord.grid(row=1, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 0))

        self.button_login = tk.Button(self, text="Login", command=self.login)
        self.button_login.grid(row=3, column=0, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

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
        naam = self.entry_naam.get()
        wachtwoord = self.entry_wachtwoord.get()
        try:
            logging.info("Sending login data to server...")
            login_to_send = pickle.dumps(("LOGIN", (naam, wachtwoord)))
            pickle.dump(login_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Login data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")

            if commando == "OK":
                result = messagebox.showinfo("Login", "Login successful")
                if result == "ok":
                    self.current_user = naam
                    self.show_main_window()
            else:
                messagebox.showinfo("Login", "Login failed")

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

        self.label_user = tk.Label(self.top_bar, text=f"Ingelogd als: {self.current_user}")
        self.label_user.pack(side=tk.LEFT, padx=(5, 5))

        self.button_logout = tk.Button(self.top_bar, text="Logout", command=self.logout)
        self.button_logout.pack(side=tk.RIGHT, padx=(5, 5))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=1)


        # Define a list of all possible searches
        searches = [
            "Grafiek van de grootte van de appels",
            "Heeft de appel met deze rijpheid een goede kwaliteit",
            "Hoe zoet is de appel met deze zuurtegraad",
            "Hoe krokant is een appel met deze rijpheid"
        ]

        # Create tabs for each search
        for search in searches:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=search)

        # Bind the tab changed event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        

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
                self.show_search_result(selected_tab_text)
            else:
                messagebox.showinfo("Search", "Search failed")
        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_search_result(self, search):
        if search == "Grafiek van de grootte van de appels":
            # Check if the tab already exists
            existing_tab = None
            for tab_id in self.notebook.tabs():
                if self.notebook.tab(tab_id, "text") == search:
                    existing_tab = self.notebook.nametowidget(tab_id)
                    break


            if existing_tab:
                # If the tab already exists, select it and clear the existing graph
                self.notebook.select(existing_tab)
                if existing_tab.winfo_children():
                    self.clear_graph(existing_tab)
                self.show_image(self.notebook.nametowidget(existing_tab))
            else:
                # If the tab doesn't exist, create a new one and plot the graph
                tab = ttk.Frame(self.notebook, padding=2)
                self.notebook.add(tab, text=search)
                self.show_image(tab)

    def clear_graph(self, parent):
        # Destroy all widgets (i.e., the graph) inside the parent frame
        for widget in parent.winfo_children():
            widget.destroy()


    def show_image(self, parent):
        # Load an image
        img = Image.open("../size_plot.png")
        img = img.resize((1200, 800))
        img = ImageTk.PhotoImage(img)

        # Create a label to display the image
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