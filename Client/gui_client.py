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
        self.widgets_by_tab = {}

    def init_window(self):
        # toont het login scherm
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
        # stuurt de login gegevens naar de server en wacht op een antwoord van de server
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
        # toont het registratie scherm
        for widget in self.winfo_children():
            #verwijdert alle voorgaande windows
            widget.destroy()

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
        # stuurt de registratie gegevens naar de server en wacht op een antwoord van de server
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
        # toont het hoofdscherm
        logging.info("Close current window")
        for widget in self.winfo_children():
            widget.destroy()
        
        self.master.title("Main")
        self.pack(fill=tk.BOTH, expand=1)

        self.top_bar = tk.Frame(self)
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

        for search in searches:
            tab = ttk.Frame(self.notebook, padding=0)
            self.notebook.add(tab, text=search)
            self.widgets_by_tab[search] = tab

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.show_search_result("Overview")
        

    def on_tab_changed(self, event):
        # kijkt welk tablad geselecteerd is
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
        # verwqijdert alle labels zodat er geen labels van andere paginas blijven staan
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()

    def show_search_result(self, search):
        # toont de resultaten van de zoekopdracht
        for widget in self.widgets_by_tab[search].winfo_children():
            # verwijdert de widgets van een ander tablad
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
        # toont de afbeelding van de appels hun grootte
        img = Image.open("../size_plot.png")
        img = img.resize((1000, 600))
        img = ImageTk.PhotoImage(img)

        label = tk.Label(parent, text="Here you can see an overview of the size of the apples devided in good and bad quality")
        label.pack()
        label = tk.Label(parent, image=img)
        label.image = img
        label.pack()

    def show_prediction(self, parent):
        # toont het voorspellings scherm
        prediction_frame = tk.Frame(parent)
        prediction_frame.pack()

        tk.Label(prediction_frame, text="Give up some parameters to see if it's a good or bad apple:").grid(row=1, column=0, sticky=tk.E)

        tk.Label(prediction_frame, text="Size:").grid(row=2, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Weight:").grid(row=3, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Sweetness:").grid(row=4, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Crunchiness:").grid(row=5, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Juiciness:").grid(row=6, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Ripeness:").grid(row=7, column=0, sticky=tk.E)
        tk.Label(prediction_frame, text="Acidity:").grid(row=8, column=0, sticky=tk.E)

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

        self.entry_size.grid(row=2, column=1)
        self.entry_weight.grid(row=3, column=1)
        self.entry_sweetness.grid(row=4, column=1)
        self.entry_crunchiness.grid(row=5, column=1)
        self.entry_juiciness.grid(row=6, column=1)
        self.entry_ripeness.grid(row=7, column=1)
        self.entry_acidity.grid(row=8, column=1)

        self.button_predict = tk.Button(prediction_frame, text="Predict", command=self.predict)
        self.button_predict.grid(row=9, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(prediction_frame, 9, weight=1)
        tk.Grid.columnconfigure(prediction_frame, 1, weight=1)

    def predict(self):
        # stuurt de voorspellings gegevens naar de server en wacht op een antwoord van de server
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
                label = tk.Label(self, text=f"The apple has a {data} quality")
                label.pack()

            else:
                messagebox.showinfo("Prediction", "Prediction failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_sweetness(self, parent):
        # toont het zoetigheid scherm
        prediction_frame = tk.Frame(parent)
        prediction_frame.pack()

        tk.Label(prediction_frame, text="Give up an acidity level to see if the apple is sweet:").grid(row=1, column=0, sticky=tk.E)

        tk.Label(prediction_frame, text="Acidity:").grid(row=2, column=0, sticky=tk.E)

        self.entry_acidity = tk.Entry(prediction_frame, width=40)

        self.entry_acidity.grid(row=2, column=1)
        self.entry_acidity.insert(0, "7.5")

        self.button_predict = tk.Button(prediction_frame, text="Predict", command=self.predict_sweetness)
        self.button_predict.grid(row=3, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(prediction_frame, 3, weight=1)
        tk.Grid.columnconfigure(prediction_frame, 3, weight=1)

    def predict_sweetness(self):
        # stuurt de zoetigheid gegevens naar de server en wacht op een antwoord van de server
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
                if data > 7.0:
                    label = tk.Label(self, text=f"Sweetness: {data} the apple is sour")
                else:
                    label = tk.Label(self, text=f"Sweetness: {data}, the apple is sweet")
                label.pack()

            else:
                messagebox.showinfo("Sweetness", "Sweetness failed")

        except Exception as ex:
            logging.error(f"Error: {ex}")
            messagebox.showinfo("Error", "Something has gone wrong...")

    def show_crunchiness(self, parent):
        # toont het knapperigheid scherm
        prediction_frame = tk.Frame(parent)
        prediction_frame.pack()

        tk.Label(prediction_frame, text="Give up a ripeness level to see if the apple is crunchy:").grid(row=1, column=0, sticky=tk.E)

        tk.Label(prediction_frame, text="Ripeness:").grid(row=2, column=0, sticky=tk.E)

        self.entry_ripeness = tk.Entry(prediction_frame, width=40)

        self.entry_ripeness.grid(row=2, column=1)
        self.entry_ripeness.insert(0, "8.0")

        self.button_predict = tk.Button(prediction_frame, text="Predict", command=self.predict_crunchiness)
        self.button_predict.grid(row=3, columnspan=2, pady=(0, 5), padx=(5, 5), sticky=tk.N + tk.S + tk.E + tk.W)

        tk.Grid.rowconfigure(prediction_frame, 3, weight=1)
        tk.Grid.columnconfigure(prediction_frame, 1, weight=1)

    def predict_crunchiness(self):
        # stuurt de knapperigheid gegevens naar de server en wacht op een antwoord van de server
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
                if data < 6.0:
                    label = tk.Label(self, text=f"Crunchiness: {data} the apple is soft")
                else:
                    label = tk.Label(self, text=f"Crunchiness: {data}, the apple is crunchy")
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
