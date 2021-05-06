
from scapy.all import *
import sys, os

TYPE_FWB = 0x1212
TYPE_IPV4 = 0x0800

class heartBeat(Packet):
    name = "heartBeat"
    fields_desc = [
        ShortField("pid", 0),
        ShortField("dst_id", 0)
        IntField("pkt_id",0)
    ]
    def mysummary(self):
        return self.sprintf("pid=%pid%, dst_id=%dst_id%", "pkt_id=%pkt_id")


bind_layers(Ether, heartBeat, type=TYPE_HEARTBEAT)
bind_layers(heartBeat, IP, pid=TYPE_IPV4)

