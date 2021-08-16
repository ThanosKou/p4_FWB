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
    # pkt.show()
    if fwb in pkt:
        # print(pkt[fwb].pkt_id)
        return pkt[fwb].pkt_id


def main():
    global t0
    t0 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, default='10.0.2.2',help="The destination IP address to use")
    parser.add_argument('--message', type=str, default='',help="The message to include in packet")
    parser.add_argument('--dst_id', type=int, default=None, help='The heartBeat dst_id to use, if unspecified then heartbeat header will not be included in packet')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    dst_id = args.dst_id
    iface = get_if()

    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_barebone = IP(dst=addr) / TCP(dport=1111, sport=51995) / args.message
            
    current_dst_id = 0
    acked_idx = 0
    sent_idx = 0
    while True:
        f = open("/home/thanos/tutorials/exercises/p4_FWB/dst_holder.txt", "r")
	line = f.read()
        dst_id = int(line.split()[0])
        acked_idx = int(line.split()[1])
	t0_listener = float(line.split()[2])
        f.close()
        if dst_id == 4:
            sleep(1)
            continue
        pkt = e / fwb(dst_id=dst_id, pkt_id=sent_idx+1, pid=TYPE_IPV4) /  pkt_barebone / str(time.time()-t0)
        sent_idx = sent_idx + 1
        # pkt.show()
        sendp(pkt, inter = 0.01, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
