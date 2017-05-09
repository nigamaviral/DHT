import math
import hashlib
import sys
import json
import threading
from Socket import *

class Node:
    finger_table_size = 160
    finger = []
    id = None
    successor = None
    predecessor = None
    nxt = 0
    node_address = ""

    def __init__(self):
        pass

    def __init__(self, node_address, node_port, id, successor, predecessor):
        self.node_address = node_address
        self.node_port = node_port
        hash_obj = hashlib.sha256(node_address + ':' + node_port)
        val_hex = hash_obj.hexdigest()
        self.id = int(val_hex, 16)
        self.successor = successor
        self.predecessor = predecessor
        self.finger = []
        self.nxt = 0

    def identify_key(self, key):
        hash_obj = hashlib.sha256(key)
        val_hex = hash_obj.hexdigest()
        return int(val_hex, 16) % math.pow(2, self.finger_table_size)

    def identify_node(self, address):
        hash_obj = hashlib.sha256(address)
        val_hex = hash_obj.hexdigest()
        return int(val_hex, 16) % math.pow(2, self.finger_table_size)

    def has_failed(self, address, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            return False
        except:
            print("Unable to connect")
        return True

    def closest_preceding_node(self, id):
        for i in range(self.finger_table_size, 1, -1):
            if self.id < self.finger[i] < id:
                return self.finger[i]

        return self.node_address

    def find_successor(self, id):
        if self.id < id <= self.successor.id:
            return self.successor.node_address
        else:
            new_node = self.closest_preceding_node(id)
            address_port = new_node.split(":")
            send(json.dumps(("successor", self.node_address)), address_port[0], address_port[1])

    def create(self):
        self.predecessor = None
        self.successor = self.node_address

    def join(self, ring_node):
        self.predecessor = None
        self.successor = ring_node.find_successor(self.id)

    def check_predecessor(self):
        if self.has_failed(self.predecessor.node_address, self.predecessor.port):
            self.predecessor = None

    def fix_fingers(self):
        self.nxt += 1
        if self.nxt > self.finger_table_size:
            nxt = 1
        self.finger[self.nxt] = self.find_successor(self.id + math.pow(2, self.nxt-1))

    def notify(self, node):
        if self.predecessor is None or self.predecessor.id < node.id < self.id:
            self.predecessor = node

    def store(self, key):
        key_hash = self.identify_key(key)
        store_address = self.find_successor(key_hash)
        address_port = store_address.split(":")
        send(json.dumps(("store", key)), address_port[0], address_port[1])

    def lookup(self, key, client_address, client_port):
        key_hash = self.identify_key(key)
        key_address = self.find_successor(key_hash)
        send(json.dumps(("store", key_address)), client_address, client_port)

def send(data, address, port):
    try:
        # print 'Sending %s to %s' % (data, neighbours[host])
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((address, port))
        s.sendall(data.encode('utf8'))
    except:
        print('exception while sending', sys.exc_info())

def stabilize(self):
    node = self.successor.predecessor
    if self.id < node.id < self.successor.id:
        self.successor = node
    self.successor.notify(node)

def start_listening(address, port):
    node = Node()
    print('starting server on ip %s' % address)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((address, port))
    serversocket.listen(5)

    stabilize_thread = threading.Thread(target=stabilize)
    stabilize_thread.start()

    try:
        while True:
            (clientsocket, address) = serversocket.accept()
            data_received = clientsocket.recv(4096).decode('utf8')
            data_type, data_received, sender = json.loads(data_received)
            print('%s received data $%s$ from %s' % (address, data_received, sender))

            if data_type == 'notify':
                pass
            elif data_type == 'get':
                pass
            elif data_type == 'put':
                pass
            elif data_type == 'join':
                pass
            elif data_type == 'details':
                pass
            elif data_type == 'successor':
                node.find_successor(data_received)

            clientsocket.close()
    except:
        print('in exception of %s with exception %s' % (address, sys.exc_info()))
        stop_all = True
        serversocket.close()
        stabilize_thread.join()