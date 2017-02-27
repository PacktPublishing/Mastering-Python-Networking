#!/usr/bin/env python3
from jnpr.junos import Device
from jnpr.junos.utils.config import Config

dev = Device(host='192.168.24.252', user='juniper', passwd='juniper!')

try:
    dev.open()
except Exception as err:
    print(err)
    sys.exit(1)

config_change = """
 <system>
    <host-name>master</host-name>
    <domain-name>python</domain-name>
 </system>
"""

cu = Config(dev)
cu.lock()
cu.load(config_change)
cu.commit()
cu.unlock()

dev.close()

