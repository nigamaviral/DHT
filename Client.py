import socket
import json
import sys
import random

class Client:
    def lookup(self, data):
        data = json.dumps(("lookup", data, 'client'))
        send_address, send_port = self.find_random_node(), 1234
        s = self.send(data, send_address, send_port)
        if s is not None:
            try:
                print s.recv(4096).decode('utf8')
                s.close()
            except:
                print 'Failed to get response'
            return
        print 'failed to send request'

    def store(self, data):
        data = json.dumps(("store", data, 'client'))
        send_address, send_port = self.find_random_node(), 1234
        s = self.send(data, send_address, send_port)
        if s is not None:
            try:
                print s.recv(4096).decode('utf8')
                s.close()
            except:
                print 'Failed to get response'
            return
        print 'failed to send request'

    def find_random_node(self):
        hosts = ['172.0.1.1', '172.0.1.2', '172.0.1.3', '172.0.1.4', '172.0.1.5', '172.0.1.6'] 
        return random.choice(hosts)

    def send(self, data, address, port):
        try:
            print 'Sending %s to %s' % (data, address)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((address, port))
            s.sendall(data.encode('utf8'))
            return s
        except:
            print('exception while sending', sys.exc_info())
        return None

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
    # client.start_listening("127.0.0.1", "5000")


    # Code for timing analysis
    '''
    for i in range(int(sys.argv[1])):
        client.lookup('fjg')

    for i in range(int(sys.argv[1])):
        client.store('fjg,anfd')
    '''

    while True:
        choice = input("Enter Your Choice ?\n 1) Lookup\n 2) Store\n 3) Exit\nEnter 1, 2, 3:")
        choice = int(input('Enter 1, 2, 3:'))

        if choice == 1:
            data = raw_input("Enter Data : ")
            client.lookup(data)
        elif choice == 2:
            data = raw_input("Enter Data : ")
            client.store(data)
        elif choice == 3:
            break
        else:
            print("Invalid Choice. Try Again!!!")
