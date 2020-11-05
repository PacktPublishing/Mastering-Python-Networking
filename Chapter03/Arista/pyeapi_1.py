#!/usr/bin/env python3

import pyeapi

class my_switch():
    
    def __init__(self, config_file_location, device):
        """
        Initialize the device.

        Args:
            self: (todo): write your description
            config_file_location: (str): write your description
            device: (todo): write your description
        """
        # loads the config file 
        pyeapi.client.load_config(config_file_location)
        self.node = pyeapi.connect_to(device)
        self.hostname = self.node.enable('show hostname')[0]['result']['hostname']
        self.running_config = self.node.enable('show running-config')

    def create_vlan(self, vlan_number, vlan_name):
        """
        Creates a vlan.

        Args:
            self: (todo): write your description
            vlan_number: (int): write your description
            vlan_name: (str): write your description
        """
        vlans = self.node.api('vlans')
        vlans.create(vlan_number)
        vlans.set_name(vlan_number, vlan_name)

