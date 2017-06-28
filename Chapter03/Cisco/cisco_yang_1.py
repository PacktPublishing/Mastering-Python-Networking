#!/usr/bin/env python3

from ncclient import manager
import xml.dom.minidom

host = "ios-xe-mgmt.cisco.com"
username = "root"
password = "C!sc0123"
port = 10000

yang_file = "cisco_yang_1_interfaces.xml"

conn = manager.connect(host=host, port=port, username=username, password=password, hostkey_verify=False, device_params={'name': 'default'}, allow_agent=False, look_for_keys=False)

with open(yang_file) as f: 
    output = (conn.get_config('running', f.read()))

print(xml.dom.minidom.parseString(output.xml).toprettyxml())


