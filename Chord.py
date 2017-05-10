import socket
import sys
import json

# for unbuffered logging
class Unbuffered(object):
   def __init__(self, stream):
        self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)
sys.stdout = Unbuffered(sys.stdout)


def add_node(address, port):
    data = json.dumps(("join", address, port))
    send_address, send_port = find_random_node()
    send(data, send_address, send_port)


def remove_node(address, port):
    #Don't send message to chord.
    pass


def display_details(address, port):
    data = json.dumps(("details", address, port))
    send_address, send_port = find_random_node()
    send(data, send_address, send_port)


def send(data, address, port):
    try:
        # print 'Sending %s to %s' % (data, neighbours[host])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, port))
        s.sendall(data.encode('utf8'))
    except:
        print('exception while sending', sys.exc_info())


def start_listening(address, port):
    print ('starting server on ip %s' % address)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((address, port))
    serversocket.listen(10)

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
    name = sys.argv[1]
    ip = sys.argv[2]
    parent = sys.argv[3]
    parent_ip = sys.argv[4]

    start_listening(ip, 1234)
