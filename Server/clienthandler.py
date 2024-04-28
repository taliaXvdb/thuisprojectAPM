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
            self.print_bericht_gui_server(f"Commando received: {commando}")

            if commando == "CLOSE":
                break

            message, data = pickle.loads(commando)
            
            if message == "LOGIN":
                naam, wachtwoord = data
                self.print_bericht_gui_server("Login...")
                self.login(naam, wachtwoord)

            elif message == "SEARCH":
                search = data
                self.print_bericht_gui_server("Search...")
                self.search(search)

        self.print_bericht_gui_server("Connection with client closed...")
        self.socket_to_client.close()



    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")
    
    def login(self, naam, wachtwoord):
        if naam == "admin" and wachtwoord == "admin":
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()
        else:
            self.print_bericht_gui_server(f"NOK")
            pickle.dump("NOK", self.socket_to_client)
            self.socket_to_client.flush()
        return
    
    def search(self, search):
        self.print_bericht_gui_server(f"Search {search}")
        usedbase = pd.read_csv("./Data/usedbase.csv")

        if search == "Overview":
            self.print_bericht_gui_server("wauw grafiek")
            usedbase['Overview'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        elif search == "Prediction":
            self.print_bericht_gui_server("wauw kwaliteit")
            usedbase['Prediction'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        elif search == "Sweetness":
            self.print_bericht_gui_server("wauw zoet")
            usedbase['Sweetness'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        elif search == "Crunchiness":
            self.print_bericht_gui_server("wauw krokant")
            usedbase['Crunchiness'] += 1
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()

        usedbase.to_csv("./Data/usedbase.csv", index=False)

        return
    
