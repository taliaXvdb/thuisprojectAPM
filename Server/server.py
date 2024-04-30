import logging
import socket
import threading
from queue import Queue
import sys
from pathlib import Path
import pandas as pd
print(sys.path[0])                  #test
sys.path[0] = str(Path(sys.path[0]).parent)      #Hier aanpassen
print(sys.path[0])    
from server.clienthandler import ClientHandler


class ProjectServer(threading.Thread):
    def __init__(self, host, port, messages_queue):
        threading.Thread.__init__(self, name="Thread-Server", daemon=True)
        self.serversocket = None
        self.__is_connected = False
        self.host = host
        self.port = port
        self.clients = []
        self.lock = threading.Lock()
        self.messages_queue = messages_queue
        self.addr = None

    @property
    def is_connected(self):
        return self.__is_connected

    def init_server(self):
        # create a socket object
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.__is_connected = True
        self.print_bericht_gui_server("SERVER STARTED")
        logged_in = pd.read_csv("./Data/logged_in.csv")
        logged_in.iloc[0:0].to_csv("./Data/logged_in.csv", index=False)

    def stop_server(self):
        if self.serversocket is not None:
            self.serversocket.close()
            self.serversocket = None
            self.__is_connected = False
            logging.info("Serversocket closed")

    # thread-klasse!
    def run(self):
        number_received_message = 0
        try:
            while True:
                logging.debug("Server waiting for a new client")
                self.print_bericht_gui_server("waiting for a new client...")

                # establish a connection
                socket_to_client, addr = self.serversocket.accept()
                self.addr = addr
                self.print_bericht_gui_server(f"Got a connection from {addr}")
                self.clh = ClientHandler(socket_to_client, self.messages_queue)
                self.clh.start()
                self.print_bericht_gui_server(f"Current Thread count: {threading.active_count()}.")
                with self.lock:
                    self.clients.append(self.clh)

        except Exception as ex:
            self.print_bericht_gui_server("Serversocket afgesloten")
            logging.debug("Thread server ended")

    def get_clients(self):
        with self.lock:
            return [self.get_info() for client in self.clients]
        
    def get_client_data(self, client_id):
        with self.lock:
            for client in self.clients:
                if client.id == client_id:
                    return client.get_info()
        return None
    
    def send_message_to_client(self, client_id, message):
        with self.lock:
            for client in self.clients:
                if client.id == client_id:
                    client.send_message(message)
                    return True
        return False
        
    def shutdown(self):
        self.stop_server()
        with self.lock:
            for client in self.clients:
                client.shutdown()
    
    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH :> {message}")

    def get_info(self):
        username = self.clh.get_username()
        logged_in = pd.read_csv("./Data/logged_in.csv")
        print(logged_in)
        new_data = pd.DataFrame({'Username': username, 'IP': self.addr[0], 'Port': self.port}, index=[0])
        logged_in = pd.concat([logged_in, new_data], ignore_index=True)
        logged_in.to_csv("./Data/logged_in.csv", index=False)
