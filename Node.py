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
        self.nxt = 0
        self.max_val = 2 ** self.finger_table_size
        if node_address != parent_ip:
            self.join(parent_name, parent_ip)
        self.global_lock = threading.Lock()
        self.finger = [(None, None, None) for i in range(self.finger_table_size)]
        self.finger[0] = self.successor
        self.hash_map = {}
        time.sleep(2)

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
        s += '%s, %s %s\n' % (self.predecessor[0], self.predecessor[1], self.predecessor[2])
        i = 1
        for finger in self.finger:
            s += '%s, %s, %s %s\n' % (i, finger[0], finger[1], finger[2])
            i += 1
        f.write(s)
        f.close()

    def has_failed(self, address, port=1234):
        return False
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            s.sendall(json.dumps(('ping', '', self.node_name)).encode('utf8'))
            return False
        except:
            print("Unable to connect")
        return True

    def inrange(self, c, a, b):
        # c -> (a, b]
        if a < b:
            return a < c <= b
        return a < c or c <= b

    def closest_preceding_node(self, id):
        for i in range(self.finger_table_size - 1, -1, -1):
            if self.inrange(self.finger[i][2], self.id, id) and not self.has_failed(self.finger[i][1]):
                return self.finger[i]

        return (self.node_name, self.node_address, self.id)

    def find_successor(self, id, base_node_address=None, base_node_name=None):
        if self.predecessor[1] is not None and self.inrange(id, self.predecessor[2], self.id):
            print 'found as predecessor for req', base_node_address, 'from', self.node_name
            return (self.node_name, self.node_address, self.id)

        if base_node_address is None:
            if self.inrange(id, self.id, self.successor[2]):
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
        s = self.send(json.dumps(('successor', id, node_name)), remote_address, self.port)
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
        s = self.send(json.dumps(('predecessor', '', self.node_name)), remote_address, self.port)
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
            self.send(json.dumps(('notify', self.id, self.node_name)), remote_address, self.port)
        pass

    def stabilize(self):
        print 'in stabilize!'
        while self.stop_all is False:
            time.sleep(2)
            self.global_lock.acquire()
            successor = self.finger[0]
            pred_of_succ = self.find_predecessor_remote(self.successor[1])
            if pred_of_succ[1] is not None and self.inrange(pred_of_succ[2], self.id, successor[2]) and \
                    (self.id + 1) != successor[2] and not self.has_failed(pred_of_succ[1]):
                self.finger[0] = pred_of_succ
                self.successor = pred_of_succ
            self.global_lock.release()
            if self.successor[1] is not None and self.successor[1] != self.node_address:
                self.notify_remote(self.successor[1])

            self.disp_details()
            pass
        print 'finished'

    def join(self, ring_node_name, ring_node_address):
        time.sleep(2)
        print 'about to call for successor to ', ring_node_address
        self.successor = self.find_successor(self.id, ring_node_address, ring_node_name)
        print 'received ', self.successor[0], 'as successor on join'

    def check_predecessor(self):
        print 'in check predecessor'
        while self.stop_all is False:
            time.sleep(2)
            if self.predecessor[1] is None:
                continue
            if self.has_failed(self.predecessor[1], self.port):
                self.predecessor = (None, None, None)
        print 'finished check predecessor'

    def fix_fingers(self):
        print 'in fix fingers'
        while self.stop_all is False:
            time.sleep(2)
            self.global_lock.acquire()
            next_id = (self.id + (2 ** self.nxt)) % (2 ** self.finger_table_size)
            self.finger[self.nxt] = self.find_successor(next_id)
            self.nxt = (self.nxt + 1) % self.finger_table_size
            self.global_lock.release()
            pass
        print 'finished fix fingers'

    def notify(self, node_name, node_address, node_id):
        print 'received new predecessor for ', self.node_name, 'ie', node_address
        if node_address == self.node_address:
            return
        if self.predecessor[1] is None or self.inrange(node_id, self.predecessor[2], self.id) or \
                self.has_failed(self.predecessor[1]):
            self.predecessor = (node_name, node_address, node_id)

        self.global_lock.acquire()
        for i in range(self.finger_table_size):
            next_id = (self.id + (2 ** i)) % self.max_val
            if self.finger[i][2] is None:
                if next_id <= node_id:
                    self.finger[i] = (node_name, node_address, node_id)
            elif self.finger[i][2] > node_id:
                self.finger[i] = (node_name, node_address, node_id)
        self.global_lock.release()
        pass

    def put(self, key, value):
        self.hash_map[key] = value

    def get(self, key):
        return self.hash_map.get(key, 'Not found')

    def store(self, key, value):
        key_hash = self.identify_key(key)
        store_address = self.find_successor(key_hash)
        key_value = ','.join([key, value])
        s = self.send(json.dumps(("put", key_value, self.node_name)), store_address[1], 1234)
        if s is not None:
            return True
        return False

    def lookup(self, key):
        if self.hash_map.get(key) is not None:
            return self.hash_map[key]
        key_hash = self.identify_key(key)
        key_address = self.find_successor(key_hash)
        s = self.send(json.dumps(("get", key, self.node_name)), key_address[1], 1234)
        if s is not None:
            response = s.recv(4096).decode('utf8')
            return response
        return 'Not found'

    def send(self, data, address, port):
        try:
            # print 'Sending %s to %s' % (data, neighbours[host])
            if address is None:
                return None
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((address, port))
            s.sendall(data.encode('utf8'))
            return s
        except:
            print('exception while sending', sys.exc_info(), 'for', data, 'at', address)

