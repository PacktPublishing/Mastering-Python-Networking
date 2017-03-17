#!/usr/bin/env python3

import sys, re

for line in iter(sys.stdin.readline, ''):
    if re.search('agent ', line):
         print(line.strip())


