import threading

import pickle
import pandas as pd


class ClientHandler(threading.Thread):
    numbers_clienthandlers = 0

    def __init__(self, socketclient, messages_queue):
        threading.Thread.__init__(self)
        # connectie with client
        self.socket_to_client = socketclient
        # message queue -> link to gui server
        self.messages_queue = messages_queue
        # id clienthandler
        self.id = ClientHandler.numbers_clienthandlers
        ClientHandler.numbers_clienthandlers += 1

    def run(self):
        self.socket_to_client = self.socket_to_client.makefile(mode='rwb')

        while True:
            commando = pickle.load(self.socket_to_client)
            print(commando)

            if commando == "CLOSE":
                break

            message, data = pickle.loads(commando)
            
            if message == "LOGIN":
                username, password = data
                self.print_bericht_gui_server("Login...")
                self.login(username, password)

            elif message == "REGISTER":
                username, password = data
                self.print_bericht_gui_server("Register...")
                self.register(username, password)

            elif message == "SEARCH":
                search = data
                self.print_bericht_gui_server("Search...")
                self.search(search)

        self.print_bericht_gui_server("Connection with client closed...")
        self.socket_to_client.close()



    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")
    
    def login(self, username, password):
        userbase = pd.read_csv("./Data/userbase.csv")

        if username in userbase['Username'].values and password in userbase['Password'].values:
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        else:
            self.print_bericht_gui_server(f"Login failed")
            pickle.dump("Login failed", self.socket_to_client)
            self.socket_to_client.flush()

        return
    
    def register(self, username, password):
        userbase = pd.read_csv("./Data/userbase.csv")

        if username in userbase['Username'].values:
            self.print_bericht_gui_server("Username already exists")
            pickle.dump("Username already exists", self.socket_to_client)
            self.socket_to_client.flush()
        else:
            # Create a new DataFrame with the new data and concatenate it with the existing DataFrame
            new_data = pd.DataFrame({'Username': [username], 'Password': [password]})
            userbase = pd.concat([userbase, new_data], ignore_index=True)
            userbase.to_csv("./Data/userbase.csv", index=False)
            self.print_bericht_gui_server("OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        return

    
    def search(self, search):
        self.print_bericht_gui_server(f"Search {search}")
        usedbase = pd.read_csv("./Data/usedbase.csv")

        if search == "Overview":
            usedbase['Overview'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        elif search == "Prediction":
            usedbase['Prediction'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        elif search == "Sweetness":
            usedbase['Sweetness'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        elif search == "Crunchiness":
            usedbase['Crunchiness'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        usedbase.to_csv("./Data/usedbase.csv", index=False)

        return
    
