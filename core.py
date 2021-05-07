#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse
import time
from time import sleep

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
    pkt.show()
    if fwb in pkt:
        # print(pkt[fwb].pkt_id)
        return pkt[fwb].pkt_id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    parser.add_argument('message', type=str, help="The message to include in packet")
    parser.add_argument('--dst_id', type=int, default=None, help='The heartBeat dst_id to use, if unspecified then heartbeat header will not be included in packet')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    dst_id = args.dst_id
    iface = get_if()

    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_barebone = IP(dst=addr) / TCP(dport=1234, sport=51995) / args.message
            
    current_dst_id = 0
    acked_idx = 0
    sent_idx = 0
    while True:       
        while sent_idx < (acked_idx + 10):
            # send a packet setting the pkt index sent+1 number of packets here using current_dst_id
            pkt = e / fwb(dst_id=dst_id, pkt_id=sent_idx+1, pid=TYPE_IPV4) /  pkt_barebone
            # pkt.show()
            sleep(0.2)
            sendp(pkt, iface=iface, verbose=False)
            pkt.show()
            # sleep(1)
            sent_idx = sent_idx + 1
            incoming_packet = sniff(iface = iface, count=1)[0]
            # incoming_packet.show()
            acked_idx = incoming_packet[fwb].pkt_id
        incoming_packet = sniff(iface = iface, count=1)[0]
        incoming_packet.show()
        acked_idx = incoming_packet[fwb].pkt_id
            # acked_idx = sniff(iface = iface, prn = lambda x: handle_pkt(x))
        # acked_idx = sniff(iface = iface, count=1)
        # acked_idx.show()



if __name__ == '__main__':
    main()