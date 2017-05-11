import math
import hashlib
import sys
import json
import threading
import socket
import time

# node name, node address, id

class Node:
    finger_table_size = 160

    def __init__(self, node_name, node_address, port, parent_name, parent_ip):
        self.node_name = node_name
        self.port = port
        self.stop_all = False
        self.node_address = node_address
        self.id = self.identify_key(node_address)
        self.successor = (node_name, node_address, self.id)
        self.predecessor = (None, None, None)
        self.finger = [(None, None, None) for i in range(self.finger_table_size)]
        self.nxt = 0
        if node_address != parent_ip:
            self.join(parent_name, parent_ip)
        self.finger[0] = self.successor

    def identify_key(self, key):
        hash_obj = hashlib.sha1(key)
        val_hex = hash_obj.hexdigest()
        return int(val_hex, 16) % (2 ** self.finger_table_size)

    def identify_node(self, address):
        hash_obj = hashlib.sha1(address)
        val_hex = hash_obj.hexdigest()
        return int(val_hex, 16) % math.pow(2, self.finger_table_size)

    def disp_details(self):
        print 'writing to file'
        f = open(self.node_name + '.txt', 'w')
        s = '%s, %s %s\n' % (self.node_name, self.node_address, self.id)
        s += '%s, %s %s\n' % (self.successor[0], self.successor[1], self.successor[2])
        s += '%s, %s %s\n' % (self.predecessor[0], self.predecessor[1], self.predecessor[2])
        f.write(s)
        f.close()

    def has_failed(self, address, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            s.sendall(json.dumps(('ping', '', self.node_name)).encode('utf8'))
            return False
        except:
            print("Unable to connect")
        return True

    def closest_preceding_node(self, id):
        for i in range(self.finger_table_size - 1, -1, -1):
            if self.id < self.finger[i][2] <= id:
                return self.finger[i]

        return (self.node_name, self.node_address, self.id)

    def find_successor(self, id, base_node_address=None, base_node_name=None):
        if base_node_address is None:
            if self.id < id <= self.successor[2]:
                return self.successor
            else:
                new_node = self.closest_preceding_node(id)
                if (new_node[1] != self.node_address):
                    return self.find_successor_remote(new_node[1], base_node_name, id, self.node_name)
                # print 'couldn\'t find successor for ', id
                return self.successor
        else:
            return self.find_successor_remote(base_node_address, base_node_name, id, self.node_name)

    def find_successor_remote(self, remote_address, base_node_name, id, node_name):
        s = send(json.dumps(('successor', id, node_name)), remote_address, self.port)
        if s is None:
            print 'didn\'t get successor'
            return (base_node_name, remote_address, self.identify_key(remote_address))

        print 'sent successor req for ', id, 'to', remote_address
        data_received = s.recv(4096).decode('utf8')
        print 'received data ', data_received
        successor = json.loads(data_received)
        s.close()
        return successor

    def find_predecessor_remote(self, remote_address):
        s = send(json.dumps(('predecessor', '', self.node_name)), remote_address, self.port)
        if s is None:
            return (None, None, None)
        print 'sent predecessor req to ', remote_address
        data_received = s.recv(4096).decode('utf8')
        print 'received data ', data_received
        predecessor = json.loads(data_received)
        s.close()
        return predecessor

    def notify_remote(self, remote_address):
        if remote_address is not None:
            send(json.dumps(('notify', self.id, self.node_name)), remote_address, self.port)
        pass

    def stabilize(self):
        print 'in stabilize!'
        while self.stop_all is False:
            # time.sleep(1)
            self.disp_details()
            if self.successor[1] == self.node_address:
                continue
            pred_of_succ = self.find_predecessor_remote(self.successor[1])
            successor = self.successor
            if self.id < pred_of_succ[2] <= self.successor[2]:
                successor = pred_of_succ
            self.notify_remote(successor[1])

            pass
        print 'finished'

    def join(self, ring_node_name, ring_node_address):
        self.predecessor = (None, None, None)
        time.sleep(1)
        self.successor = self.find_successor(self.id, ring_node_address, ring_node_name)

    def check_predecessor(self):
        print 'in check predecessor'
        while self.stop_all is False:
            # time.sleep(2)
            if self.predecessor[1] is None:
                continue
            if self.has_failed(self.predecessor[1], self.port):
                self.predecessor = (None, None, None)
        print 'finished check predecessor'

    def fix_fingers(self):
        print 'in fix fingers'
        while self.stop_all is False:
            # time.sleep(2)
            next_id = self.id + (2 ** self.nxt)
            self.finger[self.nxt] = self.find_successor(next_id)
            self.nxt = (self.nxt + 1) % self.finger_table_size
            pass
        print 'finished fix fingers'

    def notify(self, node_name, node_address, node_id):
        print 'received new predecessor for ', self.node_name, 'ie', node_address
        if (self.predecessor[1] is None) or (self.predecessor[2] < node_id <= self.id):
            self.predecessor = (node_name, node_address, node_id)
        pass

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

