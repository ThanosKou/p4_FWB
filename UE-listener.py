#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse
import numpy as np
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



# dst_id = 0 => multicast (S2 is primary, S3 is secondary)

# dst_id = 1 => multicast (S3 is primary, S2 is secondary)

# dst_id = 2 => S2 is primary, S3-UE link is down

# dst_id = 3 => S3 is primary, S2-UE link is down

# dst_id = 4 => both S2-UE and S3-UE links are down


# # prev_dst = 0, next_dst = 2
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 0, next_dst = 3
# # send a packet to S3 using control tcp port with new dst it
# target_ip = IP(dst='10.0.4.4')

# # prev_dst = 1, next_dst = 2
# # send a packet to S2 using control tcp port with new dst id
# target_ip = IP(dst='10.0.3.3') 

# # prev_dst = 1, next_dst = 3
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 2, next_dst = 0
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 2, next_dst = 4
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 3, next_dst = 1
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 3, next_dst = 4
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 4, next_dst = 2
# # send a packet to gw using control tcp port and new dst
# target_ip = IP(dst='10.0.1.1')

# # prev_dst = 4, next_dst = 3
# # send a packet to gw using control tcp port and new dst


def update_multicast(prev_dst, next_dst, last_received):
    pkt_fwb_layer = fwb(dst_id=next_dst, pkt_id=last_received+1, pid=TYPE_IPV4)
    pkt_ip_layer = IP(dst='10.0.1.1')
    if prev_dst == 0 and next_dst == 3:
        pkt_ip_layer = IP(dst='10.0.4.4')
    elif prev_dst == 1 and next_dst == 2:
        pkt_ip_layer = IP(dst='10.0.3.3')
    ctrl_pkt = e / pkt_fwb_layer / pkt_ip_layer / pkt_control_bbone
    return ctrl_pkt


def handle_pkt(pkt):
    # pkt.show()
    global last_received
    global event_idx
    global transitions
    if fwb in pkt:
        if pkt[IP].dst == '10.0.2.2' and pkt[TCP].dport == 1111: # 1111 data layer
            last_received = pkt[fwb].pkt_id
            prev_dst = pkt[fwb].dst_id
            # print(last_received)
            if last_received == event_idx:
                next_dst = int(np.random.choice(np.array(transitions[prev_dst])))
                print('PKT IDX:{}, NXT_DST:{}'.format(last_received,next_dst))
                notification_pkt = update_multicast(prev_dst,next_dst,last_received)
                sendp(notification_pkt, iface=iface, verbose=False)
                if next_dst !=4:
                    event_idx = random.randint(20,30) + last_received
                if next_dst == 4:
                    sleep(1)
                    next_dst = int(np.random.choice(np.array(transitions[4])))
                    notification_pkt = update_multicast(prev_dst,next_dst,last_received)
                    sendp(notification_pkt, iface=iface, verbose=False)
                    print('PKT IDX:{}, NXT_DST:{}'.format(last_received,next_dst))
                    event_idx = random.randint(20,30) + last_received



def main():
    global iface
    global event_idx
    global transitions
    transitions = [
        [2,3],
        [2,3],
        [0,4],
        [1,4],
        [2,3]
        ]
    event_idx = random.randint(25,50)
    # how_many_events = 20
    # start_state = 1
    # states=[start_state]
    # for _ in range(how_many_events):
    #     next_state = int(
    #     np.random.choice(np.array(transitions[states[-1]]),size=1))
    #     states.append(next_state)

    # last_change_pkt_idx = 0
    # change_pkt_idx = [last_change_pkt_idx]
    # for state in states:
    #     next_pkt_idx = last_change_pkt_idx + random.randint(10,20)
    #     if state != 4:
    #         change_pkt_idx.append(next_pkt_idx)
    #         last_change_pkt_idx = next_pkt_idx
    #     else:
    #         change_pkt_idx.append(last_change_pkt_idx)
    #         last_change_pkt_idx = last_change_pkt_idx


    change_pkt_idx=np.sort(np.random.choice(np.arange(10000),size=125,replace=False))


    ifaces = filter(lambda i: 'eth0' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "UE listening: using %s" % iface
    global e
    global last_received
    global pkt_control_bbone
    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_control_bbone =  TCP(dport=2222, sport=51995) / 'Primary change'
    last_received=-1
    received_packet = sniff(iface = iface,  prn = lambda x : handle_pkt(x))




if __name__ == '__main__':
    main()




# # prev_dst = 0, next_dst = 2
# # prev_dst = 0, next_dst = 3
# # prev_dst = 1, next_dst = 2
# # prev_dst = 1, next_dst = 3
# # prev_dst = 2, next_dst = 0
# # prev_dst = 2, next_dst = 4
# # prev_dst = 3, next_dst = 1
# # prev_dst = 3, next_dst = 4
# # prev_dst = 4, next_dst = 2
# # prev_dst = 4, next_dst = 3
