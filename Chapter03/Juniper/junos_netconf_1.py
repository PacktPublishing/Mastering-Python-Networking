#!/usr/bin/env python3

from ncclient import manager

conn = manager.connect(
        host='192.168.24.252', 
        port='830', 
        username='netconf', 
        password='juniper!',
        timeout=10,
        device_params={'name':'junos'},
        hostkey_verify=False)

result = conn.command('show version', format='text')
print(result.xpath('output')[0].text)
conn.close_session()


