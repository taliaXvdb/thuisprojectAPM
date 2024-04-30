import logging
import socket
import pickle
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk


class Window(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.init_window()
        self.make_connection_with_server()
        self.current_user = None
        self.widgets_by_tab = {}  # Dictionary to store widgets associated with each tab

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
        # Destroy widgets from the login window
        for widget in self.winfo_children():
            widget.destroy()

        # Create widgets for the registration window
        self.master.title("Register")
        self.pack(fill=tk.BOTH, expand=1)

        tk.Label(self, text="Name:").grid(row=0)
        tk.Label(self, text="Username:").grid(row=1)
        tk.Label(self, text="Email:").grid(row=2)
        tk.Label(self, text="Password:", pady=10).grid(row=3)

        self.entry_name = tk.Entry(self, width=40)
        self.entry_username = tk.Entry(self, width=40)
        self.entry_email = tk.Entry(self, width=40)
        self.entry_password = tk.Entry(self, width=40, show="*")

        self.entry_name.grid(row=0, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 5))
        self.entry_username.grid(row=1, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 5))
        self.entry_email.grid(row=2, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 5))
        self.entry_password.grid(row=3, column=1, sticky=tk.E + tk.W, padx=(5, 5), pady=(5, 0))

        self.button_register = tk.Button(self, text="Register", command=self.register_user)
        self.button_register.grid(row=4, column=0, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(self, 4, weight=1)
        tk.Grid.columnconfigure(self, 1, weight=1)


    def register_user(self):
        name = self.entry_name.get()
        username = self.entry_username.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        try:
            logging.info("Sending register data to server...")
            register_to_send = pickle.dumps(("REGISTER", (name, username, email, password)))
            pickle.dump(register_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Register data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")

            if commando == "OK":
                result = messagebox.showinfo("Register", "Register successful")
                if result == "ok":
                    self.current_user = username
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
            tab = ttk.Frame(self.notebook, padding=0)
            self.notebook.add(tab, text=search)
            self.widgets_by_tab[search] = tab  # Store the tab reference

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

    def clear_labels(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()

    def show_search_result(self, search):
        # Clear the frame associated with the current tab
        for widget in self.widgets_by_tab[search].winfo_children():
            widget.destroy()

        self.clear_labels()

        if search == "Overview":
            self.show_image(self.widgets_by_tab[search])

        elif search == "Prediction":
            self.show_prediction(self.widgets_by_tab[search])

        elif search == "Sweetness":
            self.show_sweetness(self.widgets_by_tab[search])

        elif search == "Crunchiness":
            self.show_crunchiness(self.widgets_by_tab[search])

    def show_image(self, parent):
        img = Image.open("../size_plot.png")
        img = img.resize((1000, 600))
        img = ImageTk.PhotoImage(img)

        label = tk.Label(parent, image=img)
        label.image = img
        label.pack()

    def show_prediction(self, parent):
        prediction_frame = tk.Frame(parent)
        prediction_frame.pack()

        # make a prediction by filling in all the different variables
        tk.Label(prediction_frame, text="Size:").grid(row=0, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Weight:").grid(row=1, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Sweetness:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Crunchiness:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Juiciness:").grid(row=4, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Ripeness:").grid(row=5, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Acidity:").grid(row=6, column=0, sticky=tk.E)

        self.entry_size = tk.Entry(prediction_frame, width=40)
        self.entry_size.insert(0, "7.0")
        self.entry_weight = tk.Entry(prediction_frame, width=40)
        self.entry_weight.insert(0, "85.0")
        self.entry_sweetness = tk.Entry(prediction_frame, width=40)
        self.entry_sweetness.insert(0, "8.0")
        self.entry_crunchiness = tk.Entry(prediction_frame, width=40)
        self.entry_crunchiness.insert(0, "8.0")
        self.entry_juiciness = tk.Entry(prediction_frame, width=40)
        self.entry_juiciness.insert(0, "8.0")
        self.entry_ripeness = tk.Entry(prediction_frame, width=40)
        self.entry_ripeness.insert(0, "8.0")
        self.entry_acidity = tk.Entry(prediction_frame, width=40)
        self.entry_acidity.insert(0, "7.5")

        self.entry_size.grid(row=0, column=1)
        self.entry_weight.grid(row=1, column=1)
        self.entry_sweetness.grid(row=2, column=1)
        self.entry_crunchiness.grid(row=3, column=1)
        self.entry_juiciness.grid(row=4, column=1)
        self.entry_ripeness.grid(row=5, column=1)
        self.entry_acidity.grid(row=6, column=1)

        self.button_predict = tk.Button(prediction_frame, text="Predict", command=self.predict)
        self.button_predict.grid(row=7, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(prediction_frame, 7, weight=1)
        tk.Grid.columnconfigure(prediction_frame, 1, weight=1)

    def predict(self):
        size = float(self.entry_size.get())
        weight = float(self.entry_weight.get())
        sweetness = float(self.entry_sweetness.get())
        crunchiness = float(self.entry_crunchiness.get())
        juiciness = float(self.entry_juiciness.get())
        ripeness = float(self.entry_ripeness.get())
        acidity = float(self.entry_acidity.get())

        try:
            logging.info("Sending prediction data to server...")
            prediction_to_send = pickle.dumps(("PREDICTION", (size, weight, sweetness, crunchiness, juiciness, ripeness, acidity)))
            pickle.dump(prediction_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Prediction data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")
            message, data = pickle.loads(commando)

            if message == "Predicted":
                # Show the data in the window
                label = tk.Label(self, text=f"Prediction: {data}")
                label.pack()

            else:
                messagebox.showinfo("Prediction", "Prediction failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_sweetness(self, parent):
        prediction_frame = tk.Frame(parent)
        prediction_frame.pack()

        # make a prediction by filling in all the different variables
        tk.Label(prediction_frame, text="Acidity:").grid(row=0, column=0, sticky=tk.E)

        self.entry_acidity = tk.Entry(prediction_frame, width=40)

        self.entry_acidity.grid(row=0, column=1)
        self.entry_acidity.insert(0, "7.5")

        self.button_predict = tk.Button(prediction_frame, text="Predict", command=self.predict_sweetness)
        self.button_predict.grid(row=1, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(prediction_frame, 1, weight=1)
        tk.Grid.columnconfigure(prediction_frame, 1, weight=1)

    def predict_sweetness(self):
        acidity = float(self.entry_acidity.get())

        try:
            logging.info("Sending sweetness data to server...")
            prediction_to_send = pickle.dumps(("SWEETNESS", acidity))
            pickle.dump(prediction_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Sweetness data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")
            message, data = pickle.loads(commando)

            if message == "Predicted":
                # Show the data in the window
                label = tk.Label(self, text=f"Sweetness: {data}")
                label.pack()

            else:
                messagebox.showinfo("Sweetness", "Sweetness failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_crunchiness(self, parent):
        prediction_frame = tk.Frame(parent)
        prediction_frame.pack()

        # make a prediction by filling in all the different variables
        tk.Label(prediction_frame, text="Ripeness:").grid(row=0, column=0, sticky=tk.E)

        self.entry_ripeness = tk.Entry(prediction_frame, width=40)

        self.entry_ripeness.grid(row=0, column=1)
        self.entry_ripeness.insert(0, "8.0")

        self.button_predict = tk.Button(prediction_frame, text="Predict", command=self.predict_crunchiness)
        self.button_predict.grid(row=1, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(prediction_frame, 1, weight=1)
        tk.Grid.columnconfigure(prediction_frame, 1, weight=1)

    def predict_crunchiness(self):
        ripeness = float(self.entry_ripeness.get())

        try:
            logging.info("Sending crunchiness data to server...")
            prediction_to_send = pickle.dumps(("CRUNCHINESS", ripeness))
            pickle.dump(prediction_to_send, self.in_out_server)
            self.in_out_server.flush()
            logging.info("Crunchiness data sent to server successfully")

            logging.info("Waiting for response from server...")

            commando = pickle.load(self.in_out_server)
            logging.info(f"Command received: {commando}")
            message, data = pickle.loads(commando)

            if message == "Predicted":
                # Show the data in the window
                label = tk.Label(self, text=f"Crunchiness: {data}")
                label.pack()

            else:
                messagebox.showinfo("Crunchiness", "Crunchiness failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def logout(self):
        self.close_connection()
        self.master.destroy()


logging.basicConfig(level=logging.INFO)

root = tk.Tk()
app = Window(root)
root.mainloop()
