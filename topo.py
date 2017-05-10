"""
Example topology of Quagga routers
"""

import inspect
import os
from mininext.topo import Topo
from mininext.services.quagga import QuaggaService

from collections import namedtuple

QuaggaHost = namedtuple("QuaggaHost", "name ip loIP")
net = None


class QuaggaTopo(Topo):

    "Creates a topology of Quagga routers"

    def __init__(self, total_nodes_to_create):
        """Initialize a Quagga topology with 5 routers, configure their IP
           addresses, loop back interfaces, and paths to their private
           configuration directories."""
        Topo.__init__(self)

        # Directory where this file / script is located"
        selfPath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))  # script directory

        # Initialize a service helper for Quagga with default options
        self.quaggaSvc = QuaggaService(autoStop=False)

        # Path configurations for mounts
        self.quaggaBaseConfigPath = selfPath + '/configs/'

        # List of Quagga host configs
        self.base_ip_address = [172, 0, 1, 1]
        self.subnet_mask = 16
        self.loopback_address = '127.0.0.1/24'
        self.host_prefix = 'a'
        self.total_nodes = 0

        # Add switch for IXP fabric
        self.ixpfabric = self.addSwitch('fabric-sw1')

        for i in range(total_nodes_to_create):
            self.add_node()


    def add_node(self):
        host_name, ip_address = self.get_hostname_and_ip()

        host = QuaggaHost(name=host_name, ip=ip_address,
                    loIP=self.loopback_address)

        self.increment_base_ip()

        # Create an instance of a host, called a quaggaContainer
        quaggaContainer = self.addHost(name=host.name,
                                       ip=host.ip,
                                       hostname=host.name,
                                       privateLogDir=True,
                                       privateRunDir=True,
                                       inMountNamespace=True,
                                       inPIDNamespace=True,
                                       inUTSNamespace=True)

        # Add a loopback interface with an IP in router's announced range
        self.addNodeLoopbackIntf(node=host.name, ip=host.loIP)

        # Configure and setup the Quagga service for this node
        quaggaSvcConfig = \
                {'quaggaConfigPath': self.quaggaBaseConfigPath + host.name}
        self.addNodeService(node=host.name, service=self.quaggaSvc,
                nodeConfig=quaggaSvcConfig)

        # Attach the quaggaContainer to the IXP Fabric Switch
        self.addLink(quaggaContainer, self.ixpfabric)


    def get_hostname_and_ip(self):
        host_name = self.host_prefix + str(self.total_nodes + 1)
        ip_address = '.'.join([str(term) for term in self.base_ip_address])
        ip_address += '/' + str(self.subnet_mask)
        return host_name, ip_address


    def increment_base_ip(self):
        for i in range(3, -1, -1):
            if self.base_ip_address[i] < 255:
                self.base_ip_address[i] += 1
                for j in range(i + 1, 4):
                    self.base_ip_address[j] = 1
                break
        self.total_nodes += 1



def disp_cur_nodes(net):
    print '\nCurrent nodes in the network :'
    for host in net.hosts:
        print host.name, ' - ', host.IP()
    print ''


def start_chord(net):
    cmd = 'python Chord.py %s %s %s %s >> /tmp/chord.log &'

    rand_host = net.hosts[0]
    for host in net.hosts:
        host.cmdPrint(cmd % (host.name, host.IP(), rand_host.name, rand_host.IP()))

def end_chord(net):
    for host in net.hosts:
        pid = int(host.cmd('echo $!'))
        host.cmdPrint('kill -2 %s' % pid)

def add_host(net, topo):
    print 'in add host function'
    hostname, ip_address = topo.get_hostname_and_ip()
    net.addHost(hostname)
    net.get(hostname).setIP(ip_address)
    net.addLink('fabric-sw1', hostname)
    topo.increment_base_ip()

def remove_node(net, host_name):
    print 'in remove node function'
    net.configLinkStatus('fabric-sw1', host_name, 'down')
