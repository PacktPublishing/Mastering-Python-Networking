#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel
from mininet.cli import CLI

setLogLevel( 'info' )

net = Mininet( controller=RemoteController )
c1 = net.addController('c0')

h1 = net.addHost('h1', ip='10.20.1.10/24')
h2 = net.addHost('h2', ip='10.20.1.11/24')
s1 = net.addSwitch('s1')

s1.linkTo(h1)
s1.linkTo(h2)

net.start()
s1.cmd('ovs-vsctl set-controller s1 ssl:127.0.0.1:6633')

CLI( net )
net.stop()

