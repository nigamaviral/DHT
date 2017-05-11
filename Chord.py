import socket
import sys
import json
import hashlib
import socket
from Node import *


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
        return s
    except:
        print('exception while sending', sys.exc_info())


def start_listening(address, port):
    global stop_all
    print('starting server on ip %s' % address)
    print ('%s' % parent_ip)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((address, port))
    serversocket.listen(10)

    stabilize_thread = threading.Thread(target=node.stabilize)
    stabilize_thread.start()
    fixfinger_thread = threading.Thread(target=node.fix_fingers)
    fixfinger_thread.start()
    predecessor_check_thread = threading.Thread(target=node.check_predecessor)
    predecessor_check_thread.start()

    try:
        while True:
            clientsocket, address = serversocket.accept()
            data_received = clientsocket.recv(4096).decode('utf8')
            data_type, data_received, sender = json.loads(data_received)
            print('%s received data $%s$ from %s' % (node.node_name, data_received, sender))

            if data_type == 'notify':
                node.notify(sender, address[0], int(data_received))
                pass
            elif data_type == 'get':
                pass
            elif data_type == 'put':
                pass
            elif data_type == 'join':
                pass
            elif data_type == 'details':
                print 'in details'
                node.display_details()
                pass
            elif data_type == 'successor':
                successor = node.find_successor(int(data_received))
                print node.node_name, 'sending ', successor[1], ' as successor to', sender
                clientsocket.sendall(json.dumps(successor).encode('utf8'))
            elif data_type == 'predecessor':
                predecessor = node.predecessor
                print node.node_name, 'sending ', predecessor[1], ' as predecessor to', sender
                clientsocket.sendall(json.dumps(predecessor).encode('utf8'))

            clientsocket.close()
    except:
        print('in exception of %s with exception %s' % (address, sys.exc_info()))
        print 'failed for this data', data_received
        node.stop_all = True
        serversocket.close()
        stabilize_thread.join()
        fixfinger_thread.join()
        predecessor_check_thread.join()

if __name__ == '__main__':
    name = sys.argv[1]
    ip = sys.argv[2]
    parent = sys.argv[3]
    parent_ip = sys.argv[4]
    port = 1234

    node = Node(name, ip, port, parent, parent_ip)
    start_listening(ip, port)
