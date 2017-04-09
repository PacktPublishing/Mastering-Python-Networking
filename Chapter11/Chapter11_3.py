from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

#new import
from ryu.ofproto import ether
from ryu.lib.packet import ipv4, arp


class MySimpleStaticRouter(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MySimpleStaticRouter, self).__init__(*args, **kwargs)
        self.s1_gateway_mac = '00:00:00:00:00:02'  # s1 gateway is spoofing h2
        self.s2_gateway_mac = '00:00:00:00:00:01'  # s2 gateway is spoofing h1

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

        # push out static flows, note this is priority 1
        if datapath.id == 1:
            # flow from h1 to h2
            match = parser.OFPMatch(in_port=1,
                                    eth_type=ether.ETH_TYPE_IP,
                                    ipv4_src=('192.168.1.0', '255.255.255.0'),
                                    ipv4_dst=('192.168.2.0', '255.255.255.0'))
            out_port = 2
            actions = [parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)


            # flow from h2 to h1
            match = parser.OFPMatch(in_port=2,
                                    eth_type=ether.ETH_TYPE_IP,
                                    ipv4_src=('192.168.2.0', '255.255.255.0'),
                                    ipv4_dst=('192.168.1.0', '255.255.255.0'))
            out_port = 1
            actions = [parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)

        if datapath.id == 2:
            # flow from h1 to h2
            match = parser.OFPMatch(in_port=2,
                                    eth_type=ether.ETH_TYPE_IP,
                                    ipv4_src=('192.168.1.0', '255.255.255.0'),
                                    ipv4_dst=('192.168.2.0', '255.255.255.0'))
            out_port = 1
            # Can rewrite dst mac to h2 or spoof like we have done
            # parser.OFPActionSetField(eth_dst="00:00:00:00:00:02")]
            actions = [parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)

            # from from h2 to h1
            match = parser.OFPMatch(in_port=1,
                                    eth_type=ether.ETH_TYPE_IP,
                                    ipv4_src=('192.168.2.0', '255.255.255.0'),
                                    ipv4_dst=('192.168.1.0', '255.255.255.0'))
            out_port = 2
            actions = [parser.OFPActionOutput(out_port)]
            self.add_flow(datapath, 1, match, actions)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        # Note the addition of idle_timeout and hard_timeout
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, idle_timeout=6000,
                                    hard_timeout=6000)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst,
                                    idle_timeout=6000, hard_timeout=6000)
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


