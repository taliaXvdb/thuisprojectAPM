import threading

import pickle
import pandas as pd
import hashlib


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
                name, username, email, password = data
                self.print_bericht_gui_server("Register...")
                self.register(name, username, email, password)

            elif message == "SEARCH":
                search = data
                self.print_bericht_gui_server("Search...")
                self.search(search)

            elif message == "PREDICTION":
                size, weight, sweetness, crunchiness, juiciness, ripeness, acidity = data
                self.print_bericht_gui_server("Prediction...")
                self.do_prediction(size, weight, sweetness, crunchiness, juiciness, ripeness, acidity)

            elif message == "Server Message":
                self.print_bericht_gui_server("Server message...")
                self.print_bericht_gui_server(data)
                send_message = pickle.dumps(("Server Message", data))
                pickle.dump(send_message, self.socket_to_client)
                self.socket_to_client.flush()

        self.print_bericht_gui_server("Connection with client closed...")
        self.socket_to_client.close()



    def print_bericht_gui_server(self, message):
        self.messages_queue.put(f"CLH {self.id}:> {message}")
    
    def login(self, username, password):
        userbase = pd.read_csv("./Data/userbase.csv")

        if username in userbase['Username'].values:
            # Get the hashed password corresponding to the entered username
            hashed_password = userbase.loc[userbase['Username'] == username, 'Password'].values[0]

            # Hash the entered password
            entered_password_hashed = self.hash_password(password)

            # Compare the hashed passwords
            if entered_password_hashed == hashed_password:
                self.print_bericht_gui_server("OK")
                pickle.dump("OK", self.socket_to_client)
                self.socket_to_client.flush()
                return
        self.print_bericht_gui_server("Login failed")
        pickle.dump("Login failed", self.socket_to_client)
        self.socket_to_client.flush()

        return

    
    import hashlib

    def hash_password(self, password):
        # Use SHA-256 hashing algorithm
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password

    def register(self, name, username, email, password):
        userbase = pd.read_csv("./Data/userbase.csv")

        if username in userbase['Username'].values:
            self.print_bericht_gui_server("Username already exists")
            pickle.dump("Username already exists", self.socket_to_client)
            self.socket_to_client.flush()
        else:
            # Hash the password before storing it
            hashed_password = self.hash_password(password)
            new_data = pd.DataFrame({'Name': [name], 'Username': [username], 'Email': [email], 'Password': [hashed_password]})
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
    
    def do_prediction(self, size, weight, sweetness, crunchiness, juiciness, ripeness, acidity):
        apples = pd.read_csv("./Data/apple_quality.csv")
        # search the apple with the given characteristics
        apple = apples.loc[(apples['Size'] == size) & (apples['Weight'] == weight) & (apples['Sweetness'] == sweetness) & (apples['Crunchiness'] == crunchiness) & (apples['Juiciness'] == juiciness) & (apples['Ripeness'] == ripeness) & (apples['Acidity'] == acidity)]
        # get the prediction
        prediction = apple['Quality'].values[0]
        self.print_bericht_gui_server(f"Prediction: {prediction}")
        send_prediction = pickle.dumps(("Predicted", prediction))
        pickle.dump(send_prediction, self.socket_to_client)
        self.socket_to_client.flush()
    
