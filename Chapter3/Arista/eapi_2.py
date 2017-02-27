#!/usr/bin/python2

from __future__ import print_function
from jsonrpclib import Server 
import ssl, pprint

ssl._create_default_https_context = ssl._create_unverified_context

# Run Arista commands thru eAPI
def runAristaCommands(switch_object, list_of_commands):
    response = switch_object.runCmds(1, list_of_commands)
    return response


switch = Server("https://admin:arista@192.168.199.158/command-api") 

commands = ["enable", "configure", "interface ethernet 1/3", "switchport access vlan 100", "end", "write memory"]

response = runAristaCommands(switch, commands)
pprint.pprint(response)


