#!/usr/bin/env python3
#
# Modified from Brian "devicenull" Rak's example on:
# http://blog.devicenull.org/2013/09/04/python-netflow-v5-parser.html
# 

from __future__ import print_function
import socket, struct
from socket import inet_ntoa

SIZE_OF_HEADER = 24
SIZE_OF_RECORD = 48

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 9995))

while True:
    buf, addr = sock.recvfrom(1500)

    (version, count) = struct.unpack('!HH',buf[0:4])
    (sys_uptime, unix_secs, unix_nsecs, flow_sequence) = struct.unpack('!IIII', buf[4:20])
    (engine_type, engine_id, sampling_interval) = struct.unpack('!BBH', buf[20:24])
    print(  "Headers: ",
            "\nNetFlow Version: " + str(version), 
            "\nFlow Count: " + str(count), 
            "\nSystem Uptime: " + str(sys_uptime), 
            "\nEpoch Time in seconds: " + str(unix_secs), 
            "\nEpoch Time in nanoseconds: " + str(unix_nsecs), 
            "\nSequence counter of total flow: " + str(flow_sequence), 
          )

    #Can also use socket.htohl() to convert network to host byte order 
    #uptime = socket.ntohl(struct.unpack('I',buf[4:8])[0])
    #epochseconds = socket.ntohl(struct.unpack('I',buf[8:12])[0])

    #Flowdata
    nfdata = {}
    for i in range(0, count):
        try:
            base = SIZE_OF_HEADER+(i*SIZE_OF_RECORD)

            data = struct.unpack('!IIIIHH',buf[base+16:base+36])
            input_int, output_int = struct.unpack('!HH', buf[base+12:base+16])
            nfdata[i] = {}
            nfdata[i]['saddr'] = inet_ntoa(buf[base+0:base+4])
            nfdata[i]['daddr'] = inet_ntoa(buf[base+4:base+8])
            nfdata[i]['pcount'] = data[0]
            nfdata[i]['bcount'] = data[1]
            nfdata[i]['stime'] = data[2]
            nfdata[i]['etime'] = data[3]
            nfdata[i]['sport'] = data[4]
            nfdata[i]['dport'] = data[5]
            print(i, " {0}:{1} -> {2}:{3} {4} packts {5} bytes".format(
                nfdata[i]['saddr'], 
                nfdata[i]['sport'], 
                nfdata[i]['daddr'], 
                nfdata[i]['dport'], 
                nfdata[i]['pcount'],
                nfdata[i]['bcount']),
                )

        except:
            print("Failed to parse flow record: " + str(i))
            continue

    print("*" * 10)
