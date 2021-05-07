#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse
import time
from time import sleep
import os

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from fwb_header import fwb
from fwb_header import TYPE_FWB,TYPE_IPV4

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

## We can randomize this function later on for various cases
def change_primary(prev_dst):
    next_dst = prev_dst
    if prev_dst == 0:
        next_dst = 3
    return next_dst, next_event_packet






def handle_pkt(pkt):
    # pkt.show()
    global last_received
    if fwb in pkt:
        if pkt[IP].dst == '10.0.2.2':
            last_received = pkt[fwb].pkt_id
            print(last_received)
            if last_received == 30:
                next_dst = 2
                notification_pkt = e / fwb(dst_id=next_dst,
                 pkt_id=last_received+1, pid=TYPE_IPV4) / IP(dst='10.0.3.3') / pkt_barebone
                notification_pkt.show()
                sendp(notification_pkt, iface=iface, verbose=False)





def main():
    global iface
    ifaces = filter(lambda i: 'eth0' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "UE listening: using %s" % iface
    global e
    global last_received
    global pkt_barebone
    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_barebone =  TCP(dport=1111, sport=51995) / 'Primary change'
    last_received=-1
    received_packet = sniff(iface = iface,  prn = lambda x : handle_pkt(x))




if __name__ == '__main__':
    main()
