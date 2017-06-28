#!/usr/bin/env python3

import glob, re
from graphviz import Digraph, Source

pattern = re.compile('Gi0/[1234]')

device_lldp_neighbors = []

# walk thru files in ./tmp directory
for file_name in glob.glob('tmp/*'):
    # device name
    device = file_name.split('/')[1].split('_')[0]
    print("device: " + device)
    with open(file_name, 'r') as f:
        for line in f.readlines():
            line = eval(line) #eval the line as list
            for item in line[0]:
                # only look for GigEth other than Gi0/0
                if re.search(pattern, item):
                    print("  neighbors: " + item.split()[0].split('.')[0])
                    device_lldp_neighbors.append((device, item.split()[0].split('.')[0]))

print("*" * 10)
print("Edges: " + str(device_lldp_neighbors))

my_graph = Digraph("My_Network")
my_graph.edge("Client", "r6-edge")
my_graph.edge("r5-tor", "Server")

# construct the edge relationships
for neighbors in device_lldp_neighbors:
    node1, node2 = neighbors
    my_graph.edge(node1, node2)

# Insert arbitrary DOT language commands
# such as the rank=same command
source = my_graph.source
original_text = "digraph My_Network {"
new_text = 'digraph My_Network {\n{rank=same Client "r6-edge"}\n{rank=same r1 r2 r3}\n'
new_source = source.replace(original_text, new_text)
print(new_source)
new_graph = Source(new_source)
new_graph.render("output/chapter8_lldp_graph.gv")

