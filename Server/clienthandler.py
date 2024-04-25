import threading

import pickle


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

        self.print_bericht_gui_server("Waiting for login...")
        commando = pickle.load(self.socket_to_client)
        print(commando)

        while commando != "CLOSE":
            self.print_bericht_gui_server(f"Commando received: {commando}")
            message, (naam, wachtwoord) = pickle.loads(commando)

            self.print_bericht_gui_server(f"Message received: {message} {naam} {wachtwoord}")

            if message == "LOGIN":
                self.print_bericht_gui_server("Login...")
                self.login(naam, wachtwoord)

        self.print_bericht_gui_server("Connection with client closed...")
        self.socket_to_client.close()

    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")

    def get_info(self):
        return {
            "id": self.id,
            "status": "Active" if self.is_alive() else "Inactive"
        }
    
    def login(self, naam, wachtwoord):
        self.print_bericht_gui_server(f"Login {naam} {wachtwoord}")
        print("DEBUG:", naam, wachtwoord)
        if naam == "admin" and wachtwoord == "admin":
            self.print_bericht_gui_server(f"OK")
            pickle.dump("OK", self.socket_to_client)
            self.socket_to_client.flush()
        else:
            self.print_bericht_gui_server(f"NOK")
            pickle.dump("NOK", self.socket_to_client)
            self.socket_to_client.flush()
        self.print_bericht_gui_server(f"Login {naam} {wachtwoord}")
        return
