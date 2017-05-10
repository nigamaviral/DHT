#!/usr/bin/python

"""
Example network of Quagga routers
(QuaggaTopo + QuaggaService)
"""

import sys
import atexit

# patch isShellBuiltin
import mininet.util
import mininext.util
mininet.util.isShellBuiltin = mininext.util.isShellBuiltin
sys.modules['mininet.util'] = mininet.util

from mininet.util import dumpNodeConnections
from mininet.node import OVSController
from mininet.log import setLogLevel, info

from mininext.cli import CLI
from mininext.net import MiniNExT

from topo import QuaggaTopo
from topo import *
import time

import pdb

net = None

def startNetwork():
    "instantiates a topo, then starts the network and prints debug information"

    total_nodes = int(sys.argv[1]) if len(sys.argv) > 1 else 6

    info('** Creating Quagga network topology\n')
    topo = QuaggaTopo(total_nodes)

    info('** Starting the network\n')
    global net
    net = MiniNExT(topo, controller=OVSController)
    net.start()

    info('** Dumping host connections\n')
    dumpNodeConnections(net.hosts)

    info('** Testing network connectivity\n')
    net.ping(net.hosts)

    info('** Dumping host processes\n')
    for host in net.hosts:
        host.cmdPrint("ps aux")

    info('** Running CLI\n')
    # pdb.set_trace()
    # CLI(net)

    # import pdb; pdb.set_trace()

    start_chord(net)

    while True:
        disp_cur_nodes(net)
        print "1. Add Node"
        print "2. Remove Node"
        print "3. Details of Node"
        print "4. Lookup"
        print "5. Store"
        print "6. Exit"

        choice = int(input("Please enter your choice : "))

        if choice == 1:
            add_host(net)
            print 'in add node'
        elif choice == 2:
            remove_node(net, 'a1')
            print 'in remove node'
        elif choice == 3:
            print 'in details'
        elif choice == 4:
            print 'in lookup'
        elif choice == 5:
            print 'in store'
        elif choice == 6:
            end_chord(net)
            print 'exiting'
            time.sleep(1)
            break
        else:
            print 'Invalid choice, please try again'

def stopNetwork():
    "stops a network (only called on a forced cleanup)"

    if net is not None:
        info('** Tearing down Quagga network\n')
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
