#!/usr/env/bin python

#https://www.spamhaus.org/drop/drop.txt

import logging, pprint, re
import requests, json, datetime
from collections import OrderedDict

#logging configuration
logging.basicConfig(filename='/home/echou/Master_Python_Networking/Chapter8/tmp/spamhaus_drop_list.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%b %d %I:%M:%S')
host = 'python_networkign'
process = 'spamhause_drop_list'

r = requests.get('https://www.spamhaus.org/drop/drop.txt')
result = r.text.strip()

timeInUTC = datetime.datetime.utcnow().isoformat()
Item = OrderedDict()
Item["Time"] = timeInUTC

for line in result.split('\n'):
    if re.match('^;', line) or line == '\r': # comments
        next
    else:
       ip, record_number = line.split(";")
       logging.warning(host + ' ' + process + ': ' + 'src_ip=' + ip.split("/")[0] + ' record_number=' + record_number.strip())


