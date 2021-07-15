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
import subprocess

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
    if fwb in pkt and pkt[TCP].dport==2222 and pkt[TCP].sport!= 3333: # 2222 is control tcp ports
        # pkt.show()
        f = open("/home/thanos/tutorials/exercises/p4_FWB/3gpp_dst_holder.txt", "r")
        line = f.read()
        prev_dst = int(line.split()[0])
        acked_idx = int(line.split()[1])
        f.close()
        # print('reached hereeee')
        f = open("/home/thanos/tutorials/exercises/p4_FWB/3gpp_dst_holder.txt", "w")
        write_string = '{} {}\n'.format(pkt[fwb].dst_id,pkt[fwb].pkt_id)
        f.write(write_string) #update the multicast tree
        f.close()
        # send control acknowledge to the origin of the packet
        notification_pkt = e / fwb(dst_id=prev_dst,
                 pkt_id=0, pid=TYPE_IPV4) / IP(dst='10.0.2.2') / pkt_control_bbone
        # notification_pkt.show()
        sendp(notification_pkt, iface=iface, verbose=False)


def main():
    global iface
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    global e
    global pkt_control_bbone
    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_control_bbone =  TCP(dport=2222, sport=3333) / 'Confirming the change'

    # while True:
        # received_packet = sniff(iface = iface,  count=1)[0]
    received_packet = sniff(iface = iface,  prn = lambda x : handle_pkt(x))
        # filter="icmp and host 66.35.250.151"
        # print(received_packet)
        # # new_dst = received_packet[fwb].dst_id
        # new_dst = received_packet
        # f = open("/home/mfo254/tutorials/exercises/p4_FWB/dst_holder.txt", "w")
        # f.write(str(new_dst))
        # f.close()



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
