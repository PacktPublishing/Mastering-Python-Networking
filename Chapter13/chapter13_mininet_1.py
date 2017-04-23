#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel
from mininet.cli import CLI

setLogLevel( 'info' )

net = Mininet( controller=RemoteController, switch=OVSKernelSwitch )
c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6633)
c2 = net.addController('c2', controller=RemoteController, ip='127.0.0.1', port=5555)

h1 = net.addHost('h1', ip='10.0.0.1')
h2 = net.addHost('h2', ip='10.0.0.2')
h3 = net.addHost('h3', ip='10.0.0.3')
h4 = net.addHost('h4', ip='10.0.0.4')
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')

s1.linkTo(h1)
s1.linkTo(h2)
s1.linkTo(s2)
s2.linkTo(h3)
s2.linkTo(h4)

net.build()

c1.start()
c2.start()
s1.start([c1,c2])
s2.start([c1,c2])

net.start()
net.staticArp()
CLI( net )
net.stop()

