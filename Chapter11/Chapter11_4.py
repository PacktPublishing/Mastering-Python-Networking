# REST API
#
# Retrieve the switch stats
#
# get the list of all switches
# GET /network/switches
#
# get the description of the switch
# GET /network/desc/<dpid>
#
# get flows stats of the switch
# GET /network/flow/<dpid>
#
# add a flow entry
# POST /network/flowentry/add
#
# delete all matching flow entries
# POST /network/flowentry/delete
#

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.ofproto import ether
from ryu.lib.packet import ipv4, arp

# new imports
from ryu.app.ofctl_rest import *


class MySimpleRestRouter(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # new
    _CONTEXTS = {
        'dpset': dpset.DPSet,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(MySimpleRestRouter, self).__init__(*args, **kwargs)
        self.s1_gateway_mac = '00:00:00:00:00:02'  # s1 gateway is spoofing h2
        self.s2_gateway_mac = '00:00:00:00:00:01'  # s2 gateway is spoofing h1

        # new
        self.dpset = kwargs['dpset']
        wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters
        mapper = wsgi.mapper

        wsgi.registory['StatsController'] = self.data
        path = '/network'

        uri = path + '/switches'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_dpids',
                       conditions=dict(method=['GET']))

        uri = path + '/desc/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_desc_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/flow/{dpid}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='get_flow_stats',
                       conditions=dict(method=['GET']))

        uri = path + '/flowentry/{cmd}'
        mapper.connect('stats', uri,
                       controller=StatsController, action='mod_flow_entry',
                       conditions=dict(method=['POST']))


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        # Note the addition of idle_timeout and hard_timeout
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']


        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Answering ARP packets for packet destined for gateways
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            arp_packet = pkt.get_protocols(arp.arp)[0]
            ethernet_src = eth.src

            # answering arp for s2 gateway 192.168.2.1
            if arp_packet.dst_ip == '192.168.2.1' and datapath.id == 2:
                print('Received ARP for 192.168.2.1')

                # building packet
                e = ethernet.ethernet(dst=eth.src, src=self.s2_gateway_mac, ethertype=ether.ETH_TYPE_ARP)
                a = arp.arp(hwtype=1, proto=0x0800, hlen=6, plen=4, opcode=2,
                            src_mac=self.s2_gateway_mac, src_ip='192.168.2.1',
                            dst_mac=ethernet_src, dst_ip=arp_packet.src_ip)

                p = packet.Packet()
                p.add_protocol(e)
                p.add_protocol(a)
                p.serialize()

                # sending arp response for s2 gateway
                outPort = in_port
                actions = [datapath.ofproto_parser.OFPActionOutput(outPort, 0)]
                out = datapath.ofproto_parser.OFPPacketOut(
                    datapath=datapath,
                    buffer_id=0xffffffff,
                    in_port=datapath.ofproto.OFPP_CONTROLLER,
                    actions=actions,
                    data=p.data)
                datapath.send_msg(out)

            # answring arp for s1 gateway 192.168.1.1
            elif arp_packet.dst_ip == '192.168.1.1' and datapath.id == 1:
                print('Received ARP for 192.168.1.1')

                # building packet
                e = ethernet.ethernet(dst=eth.src, src=self.s1_gateway_mac, ethertype=ether.ETH_TYPE_ARP)
                a = arp.arp(hwtype=1, proto=0x0800, hlen=6, plen=4, opcode=2,
                            src_mac=self.s1_gateway_mac, src_ip='192.168.1.1',
                            dst_mac=ethernet_src, dst_ip=arp_packet.src_ip)

                p = packet.Packet()
                p.add_protocol(e)
                p.add_protocol(a)
                p.serialize()

                # sending arp response for s1 gateway
                outPort = in_port
                actions = [datapath.ofproto_parser.OFPActionOutput(outPort, 0)]
                out = datapath.ofproto_parser.OFPPacketOut(
                    datapath=datapath,
                    buffer_id=0xffffffff,
                    in_port=datapath.ofproto.OFPP_CONTROLLER,
                    actions=actions,
                    data=p.data)
                datapath.send_msg(out)

        # verbose iteration of packets
        try:
            for p in pkt.protocols:
                print(p.protocol_name, p)
            print("datapath: {} in_port: {}".format(datapath.id, in_port))
        except:
            pass

    # new
    @set_ev_cls([ofp_event.EventOFPStatsReply,
                 ofp_event.EventOFPDescStatsReply,
                 ofp_event.EventOFPFlowStatsReply,
                 ofp_event.EventOFPAggregateStatsReply,
                 ofp_event.EventOFPTableStatsReply,
                 ofp_event.EventOFPTableFeaturesStatsReply,
                 ofp_event.EventOFPPortStatsReply,
                 ofp_event.EventOFPQueueStatsReply,
                 ofp_event.EventOFPQueueDescStatsReply,
                 ofp_event.EventOFPMeterStatsReply,
                 ofp_event.EventOFPMeterFeaturesStatsReply,
                 ofp_event.EventOFPMeterConfigStatsReply,
                 ofp_event.EventOFPGroupStatsReply,
                 ofp_event.EventOFPGroupFeaturesStatsReply,
                 ofp_event.EventOFPGroupDescStatsReply,
                 ofp_event.EventOFPPortDescStatsReply
                 ], MAIN_DISPATCHER)
    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
            flags = dp.ofproto.OFPSF_REPLY_MORE
        elif dp.ofproto.OFP_VERSION >= ofproto_v1_3.OFP_VERSION:
            flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()

    @set_ev_cls([ofp_event.EventOFPQueueGetConfigReply,
                 ofp_event.EventOFPRoleReply,
                 ], MAIN_DISPATCHER)
    def features_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        del self.waiters[dp.id][msg.xid]
        lock.set()



