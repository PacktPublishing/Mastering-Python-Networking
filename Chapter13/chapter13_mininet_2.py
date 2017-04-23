#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel
from mininet.cli import CLI

setLogLevel( 'info' )

net = Mininet( controller=RemoteController, switch=OVSKernelSwitch )
c1 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=5555)

h1 = net.addHost('h1', ip='10.20.1.10/24')
h2 = net.addHost('h2', ip='10.20.1.11/24')
s1 = net.addSwitch('s1')

s1.linkTo(h1)
s1.linkTo(h2)

net.build()

c1.start()
s1.start([c1])

net.start()
net.staticArp()
CLI( net )
net.stop()

