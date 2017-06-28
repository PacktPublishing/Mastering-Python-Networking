#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.dates as dates

x_time = []
y_value = []

with open('results.txt', 'r') as f:
    for line in f.readlines():
        # eval(line) reads in each line as dictionary instead of string
        line = eval(line)
        # convert to internal float 
        x_time.append(dates.datestr2num(line['Time']))
        y_value.append(line['Gig0-0_Out_uPackets'])

plt.subplots_adjust(bottom=0.3)
plt.xticks(rotation=80)

# Use plot_date to display x-axis back in date format
plt.plot_date(x_time, y_value)
plt.title('Router1 G0/0')
plt.xlabel('Time in UTC')
plt.ylabel('Output Unicast Packets')
plt.savefig('matplotlib_1_result.png')
plt.show()


