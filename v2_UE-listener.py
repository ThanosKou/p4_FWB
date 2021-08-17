#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import argparse
import numpy as np
import json
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



# dst_id = 0 => multicast (S2 is primary, S3 is secondary)

# dst_id = 1 => multicast (S3 is primary, S2 is secondary)

# dst_id = 2 => S2 is primary, S3-UE link is down

# dst_id = 3 => S3 is primary, S2-UE link is down

# dst_id = 4 => both S2-UE and S3-UE links are down

def update_multicast(prev_dst, next_dst, last_received):
    pkt_fwb_layer = fwb(dst_id=next_dst, pkt_id=last_received+1, pid=TYPE_IPV4)
    pkt_ip_layer = IP(dst='10.0.1.1')
    if prev_dst == 0 and next_dst == 3:
        #If starts to use bs2 as primary, notify BS2
        pkt_ip_layer = IP(dst='10.0.4.4')
    elif prev_dst == 1 and next_dst == 2:
        #If starts to use bs1 as primary, notify BS1
        pkt_ip_layer = IP(dst='10.0.3.3')
    ctrl_pkt = e / pkt_fwb_layer / pkt_ip_layer / pkt_control_bbone
    return ctrl_pkt

def send_t0_listener(prev_dst, next_dst, last_received,t0_listener):
    pkt_fwb_layer = fwb(dst_id=next_dst, pkt_id=last_received+1, pid=TYPE_IPV4)
    pkt_ip_layer = IP(dst='10.0.1.1')
    ctrl_pkt = e / pkt_fwb_layer / pkt_ip_layer / pkt_control_bbone_t0 / t0_listener
    return ctrl_pkt


def handle_pkt(pkt):
    global last_received
    global event_idx
    global transitions
    global a_m_idx
    global prev_dst
    global recording_file
    global t0
    global received_packets
    global UE_delay
    global transition

    if fwb in pkt:
	if pkt[IP].dst == '10.0.2.2' and pkt[TCP].dport == 2223: # confirming the change from listen_and_update
	    transition = 0
        if pkt[IP].dst == '10.0.2.2' and pkt[TCP].dport == 1111: # 1111 data layer
	    generated_time = bytes(pkt[TCP].payload)
	    if received_packets:
	    	last_received = np.max(received_packets)
	    else:
		last_received = 0
            #last_received = pkt[fwb].pkt_id
            # if last_received + 1 == pkt[fwb].pkt_id:
            if pkt[fwb].pkt_id not in received_packets:
# 		if condition about a_m_index - > foor a given ue state(prev_dst) check if prev_dst primary is correct for received packet dst.
		received_packets.append(pkt[fwb].pkt_id)
	        last_received = np.max(received_packets)
		if last_received == event_idx or transition:
             	    print('{},{},{},{}\n'.format(pkt[fwb].pkt_id,generated_time,time.time()-t0+2*UE_delay/1000,prev_dst)) 
                    recording_file.write('{},{},{},{}\n'.format(pkt[fwb].pkt_id,generated_time,time.time()-t0+2*UE_delay/1000,prev_dst))
		else:	
              	    #print('{},{},{},{}\n'.format(pkt[fwb].pkt_id,generated_time,time.time()-t0,prev_dst)) 
                    recording_file.write('{},{},{},{}\n'.format(pkt[fwb].pkt_id,generated_time,time.time()-t0,prev_dst))
                if last_received >= 8100:
                    print('Done')
                    exit()
# 		else of am index:
# 			observe packets coming here and why.
# 			these packets here are coming from previous primary bs which supposed to be blocked.
            if last_received == event_idx:
		transition = 1
                #last_received = pkt[fwb].pkt_id
                next_dst = int(np.random.choice(np.array(transitions[prev_dst])))
                print('PKT IDX:{}, NXT_DST:{}'.format(last_received,next_dst))
                event_idx = random.randint(500,510) + last_received
                notification_pkt = update_multicast(prev_dst,next_dst,last_received)
                sendp(notification_pkt, iface=iface, verbose=False)
                prev_dst = next_dst
            # else:
                # pkt.show()
                # sleep(200)


def main():
    global iface
    global event_idx
    global transitions
    global a_m_idx
    global UE_delay 
    global transition

    transition = 0
    # transitions = [[2,3],[2,3],[0,4],[1,4],[2,3]]
    transitions = [[2,3],[2,3],[0],[1],[2,3]]
    event_idx = random.randint(25,50)
    a_m_idx = [[0,2],[1,3],[2,0],[3,1],[2,3]] # acceptable multicast ...
    #destinations for a prev_dst, for example adding a secondary bs or removing the secondary bs should still be valid even if prev_dst is different
    global recording_file
    global t0
    #         f = 
    #     prev_dst = f.read() #update the multicast tree
    #     prev_dst = int(prev_dst)
    #     f.close()
    topo_file = "/home/thanos/tutorials/exercises/p4_FWB/pod-topo/topology.json"
    with open(topo_file, 'r') as f:
        topo = json.load(f)
    GW_delay = topo['links'][0][2]
    UE_delay = topo['links'][1][2]
    record_string = '/home/thanos/tutorials/exercises/p4_FWB/out_data/burst_GW_regular_loss/pkt_arrivals_{}ms_{}ms.txt'.format(GW_delay,UE_delay)
    recording_file = open(record_string, "w")
    recording_file.write('PacketSeqNo,GeneratedTime(sec),ArrivalTime(sec),MulticastIdx\n')


    ifaces = filter(lambda i: 'eth0' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "UE listening: using %s" % iface

    global e
    global last_received
    global pkt_control_bbone
    global pkt_control_bbone_t0
    global prev_dst
    global received_packets
    received_packets = []
    prev_dst = 1 #always start with case 1
    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_control_bbone =  TCP(dport=2222, sport=50002) / 'Primary change'
    pkt_control_bbone_t0 =  TCP(dport=2223, sport=50002) / ''
    t0 = time.time()
    notification_pkt = send_t0_listener(1,0,0,str(t0))
    sendp(notification_pkt, iface=iface, verbose=False)
    last_received=0
    received_packet = sniff(iface = iface,  prn = lambda x : handle_pkt(x))




if __name__ == '__main__':
    main()

