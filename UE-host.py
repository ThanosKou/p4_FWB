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


def handle_pkt(pkt):
    # pkt.show()
    if fwb in pkt:
        # print(pkt[fwb].pkt_id)
        return pkt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    parser.add_argument('message', type=str, help="The message to include in packet")
    parser.add_argument('--dst_id', type=int, default=None, help='The heartBeat dst_id to use, if unspecified then heartbeat header will not be included in packet')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    dst_id = args.dst_id
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface

    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    # e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_IPV4)
    # e.show()
    pkt_barebone = IP(dst=addr) / TCP(dport=1234, sport=51995) / args.message

    received_idx = 0
    while True:
        received_packet = sniff(iface = iface,  count=1)[0]
        sleep(0.5)
        pkt_idx = received_packet[fwb].pkt_id
        # received_packet.show()
        if received_idx <  pkt_idx:
            # e.show()    
            received_idx = pkt_idx
            pkt = e / fwb(dst_id=dst_id, pkt_id=received_idx, pid=TYPE_IPV4) /  pkt_barebone
            # pkt = e / pkt_barebone
            # pkt.show()
            pkt.show()
            sendp(pkt, iface=iface, verbose=False)
            # sleep(1)



    # current_dst_id = 0
    # acked_idx = 0
    # sent_idx = 0
    # pkt = IP(dst=addr) / TCP(dport=1234, sport=51995) / args.message
    # while True:       
    #     while current_sent < current_acked + 100:
    #         # send a packet setting the pkt index sent+1 number of packets here using current_dst_id
    #         e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    #         pkt = e / fwb(dst_id=dst_id, pkt_id=sent_idx+1) /  pkt
    #         sendp(pkt, iface=iface, verbose=False)
    #         sent_idx = sent_idx + 1
    #         sleep(0.001)
    #         # acked_idx = sniff(iface = iface, prn = lambda x: handle_pkt(x))
    #     acked_idx = sniff(iface = iface, prn = lambda x: handle_pkt(x))



if __name__ == '__main__':
    main()