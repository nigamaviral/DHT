import socket
import json
import sys


class Client:
    def lookup(self, data):
        data = json.dumps(("get", data))
        send_address, send_port = self.find_random_node()
        self.send(data, send_address, send_port)

    def store(self, data):
        data = json.dumps(("put", data))
        send_address, send_port = self.find_random_node()
        self.send(data, send_address, send_port)

    def find_random_node(self):
        pass

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
                (clientsocket, address) = serversocket.accept()
                data_received = clientsocket.recv(4096).decode('utf8')
                data_type, data_received, sender = json.loads(data_received)
                print('%s received data $%s$ from %s' % (address, data_received, sender))
                if data_type == 'lookup':
                    pass
                elif data_type == 'store':
                    pass
                clientsocket.close()
        except:
            print('in exception of %s with exception %s' % (address, sys.exc_info()))
            serversocket.close()


if __name__ == '__main__':
    client = Client()
    client.start_listening("127.0.0.1", "5000")

    while True:
        choice = (input("Enter Your Choice ?\n A) Lookup\n B) Store\n Enter A, B:"))
        data = (input("Enter Data"))

        if choice == "A":
            client.lookup(data)
        elif choice == "B":
            client.store(data)
        else:
            print("Invalid Choice. Try Again!!!")
