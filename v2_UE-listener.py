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
        #If starts to use bs2 as primary, notify BS2
        pkt_ip_layer = IP(dst='10.0.3.3')
    ctrl_pkt = e / pkt_fwb_layer / pkt_ip_layer / pkt_control_bbone
    return ctrl_pkt

def outage_to_bs(dst_bs):
    outage_to_bs = False 
    chance = (random.randint(1,100)) 
    if dst_bs < 125: # no outage
	loss_prob = 0.0000001
    elif dst_bs < 150: 
	loss_prob = 0.1
    elif dst_bs < 175: 
	loss_prob = 0.35
    elif dst_bs < 200: 
	loss_prob = 0.75
    else:
	loss_prob = 1
    if chance <= loss_prob*100:
	outage_to_bs = True
    return outage_to_bs

def new_dst_id(outage1,outage2,prev_dst):
    if prev_dst == 0 or prev_dst == 1:
	if outage1 and not outage2: # BS1 is down and BS2 is up
	    next_dst = 3
	elif not outage1 and outage2: # BS1 is up and BS2 is down
	    next_dst = 2 
	else:
	    next_dst = prev_dst
    elif prev_dst == 2 or prev_dst == 3:
	if not outage1 and not outage2:
	    next_dst = prev_dst - 2 # 3->1, 2->0
	else:
	    next_dst = prev_dst
    return next_dst


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
                if last_received >= 4000:
                    print('Done')
                    exit()
	    current_time = time.time()
            if current_time - last_time >= float(delays[row])/10:
		last_time = current_time 
		outage1 = outage_to_bs(float(dist_bs1[row]))
		outage2 = outage_to_bs(float(dist_bs2[row]))
		next_dst = new_dst_id(outage1,outage2,prev_dst) 
                print('PKT IDX:{}, NXT_DST:{}, {}, {}'.format(last_received,next_dst,outage1,outage2))
		#recording_file.write('{},{}\n'.format(last_received,time.time()-t0))
		if next_dst != prev_dst:
                    notification_pkt = update_multicast(prev_dst,next_dst,last_received)
                    sendp(notification_pkt, iface=iface, verbose=False)
                prev_dst = next_dst
		row += 1 


def main():
    global iface
    global event_idx
    global transitions
    global a_m_idx
    global UE_delay 
    global transition
    global dist_bs1
    global dist_bs2
    global delays
    global row
    global dist_bs1
    global dist_bs2
    global delays
    global row

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

    distance_file = "/home/thanos/tutorials/exercises/p4_FWB/data_analysis/realistic_loss_dist.txt"
    f=open(distance_file,"r")
    lines=f.readlines()
    dist_bs1=[]
    dist_bs2=[]
    delays=[]
    for x in lines:
	sline = x.split(",")
    	dist_bs1.append(sline[0]) #distances from BS1
    f.close()
    f=open(distance_file,"r")
    for x in lines:
	sline = x.split(",")
    	dist_bs2.append(sline[1]) #distances from BS2
    f.close()
    f=open(distance_file,"r")
    for x in lines:
	sline = x.split(",")
    	delays.append(sline[2].strip()) #time to stop 
    f.close()
    row = 1 # shows where in the realistic_loss file we are

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

