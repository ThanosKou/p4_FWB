
from scapy.all import *
import sys, os

TYPE_FWB = 0x1212
TYPE_IPV4 = 0x0800

class fwb(Packet):
    name = "fwb"
    fields_desc = [
        ShortField("pid", 0),
        ShortField("dst_id", 0),
        IntField("pkt_id",0)
    ]
    def mysummary(self):
        return self.sprintf("pid=%pid%, dst_id=%dst_id%, pkt_id=%pkt_id")


bind_layers(Ether, fwb, type=TYPE_FWB)
bind_layers(fwb, IP, pid=TYPE_IPV4)

