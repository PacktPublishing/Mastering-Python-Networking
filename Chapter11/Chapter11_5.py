import eventlet

eventlet.monkey_patch()

import logging
import sys

log = logging.getLogger()
log.addHandler(logging.StreamHandler(sys.stderr))
log.setLevel(logging.DEBUG)

from ryu.services.protocols.bgp.bgpspeaker import BGPSpeaker

def dump_remote_best_path_change(event):
    print 'the best path changed:', event.remote_as, event.prefix,\
        event.nexthop, event.is_withdraw

def detect_peer_down(remote_ip, remote_as):
    print 'Peer down:', remote_ip, remote_as

if __name__ == "__main__":
    speaker = BGPSpeaker(as_number=65000, router_id='172.16.1.174',
                         best_path_change_handler=dump_remote_best_path_change,
                         peer_down_handler=detect_peer_down)

    speaker.neighbor_add('172.16.1.175', 1)
    count = 0
    while True:
        eventlet.sleep(30)
        prefix = '10.20.' + str(count) + '.0/24'
        print "add a new prefix", prefix
        speaker.prefix_add(prefix)
        count += 1
        print("Neighbors: ", speaker.neighbors_get())
        print("Routes: ", speaker.rib_get())








