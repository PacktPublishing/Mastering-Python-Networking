#!/usr/bin/python3

import pexpect

devices = {'iosv-1': {'prompt': 'iosv-1#', 'ip': '172.16.1.189'}}
username = 'cisco'
password = 'cisco'

for device in devices.keys(): 
    device_prompt = devices[device]['prompt']
    child = pexpect.spawn('telnet ' + devices[device]['ip'])
    child.expect('Username:')
    child.sendline(username)
    child.expect('Password:')
    child.sendline(password)
    child.expect(device_prompt)
    child.sendline('sh ip access-lists permit_snmp | i 172.16.1.173')
    child.expect(device_prompt)
    output = child.before
    child.sendline('exit')

print(str(output).split('(')[1].split()[0].strip())
    
