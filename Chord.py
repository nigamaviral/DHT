import socket
import sys
import json

class Chord:
    def add_node(self, address, port):
        data = json.dumps(("join", address, port))
        send_address, send_port = self.find_random_node()
        self.send(data, send_address, send_port)

    def remove_node(self, address, port):
        #Don't send message to chord.
        pass

    def display_details(self, address, port):
        data = json.dumps(("details", address, port))
        send_address, send_port = self.find_random_node()
        self.send(data, send_address, send_port)

    def find_random_node(self):
        address = ""
        port = ""
        return address, port

    def send(self, data, address, port):
        try:
            # print 'Sending %s to %s' % (data, neighbours[host])
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            s.sendall(data.encode('utf8'))
        except:
            print('exception while sending', sys.exc_info())

    def start_listening(self, address, port):
        print('starting server on ip %s' % address)
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((address, port))
        serversocket.listen(5)

        try:
            while True:
                clientsocket, address = serversocket.accept()
                data_received = clientsocket.recv(4096).decode('utf8')
                data_type, data_received, sender = json.loads(data_received)
                print('%s received data $%s$ from %s' % (address, data_received, sender))
                clientsocket.close()
        except:
            print('in exception of %s with exception %s' % (address, sys.exc_info()))
            serversocket.close()

if __name__ == '__main__':
    chord = Chord()
    chord.start_listening("127.0.0.1", "5001")
    while True:
        choice = (input("Enter Your Choice ?\n A) Add Node\n B) Remove Node\n C) Details of Node\nEnter A, B, C:"))
        address = (input("Enter Node Address"))
        port = (input("Enter Node Port"))

        if choice == "A":
            chord.add_node(address, port)
        elif choice == "B":
            chord.remove_node(address, port)
        elif choice == "C":
            chord.display_details(address, port)
        else:
            print("Invalid Choice. Try Again!!!")