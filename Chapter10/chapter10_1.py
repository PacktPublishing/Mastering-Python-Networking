# Referenced from ryu/ryu/app/simple_switch_13.py

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, ofproto_v1_0

class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print("ev message: ", ev.msg)
        datapath = ev.msg.datapath
        print("datapath: ", datapath)
        ofproto = datapath.ofproto
        print("ofprotocol: ", ofproto)
        parser = datapath.ofproto_parser
        print("parser: ", parser)

