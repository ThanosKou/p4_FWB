#!/usr/bin/env python
import argparse
import sys
import math
import socket
import random
import struct
import argparse
import time
from time import sleep
import numpy as np

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
        return pkt[fwb].pkt_id
        # print(pkt[fwb].pkt_id)
        
def generate_traffic_model_sinusoid(mean_time, min_time_to_send):
    start_time = 1
    end_time = 2
    sample_rate = 300
    time = np.arange(start_time, end_time, 1./sample_rate)
    theta = 0
    frequency = 50
    amplitude = mean_time
    A = amplitude + np.around(amplitude * np.sin(2 * np.pi * frequency * time + theta), decimals=4)

    cumSum = [sum(A[:i+1]) for i in range(len(A))]
    depart = [0]*len(A)
    depart[0] = cumSum[0]
    for i in range(1,len(A)):
        depart[i] = max(depart[i-1] + min_time_to_send, cumSum[i])
    diff_list = []
    for x, y in zip(depart[0::], depart[1::]):
        diff_list.append(y-x)
    return [A[0]]+ diff_list

def generate_traffic_model_M_D_1(mean_time, min_time_to_send):
    _lambda = 1.0 / mean_time
    num_events = 8000
    inter_event_times = []

    for i in range(num_events):
        #Get a random probability value from the uniform distribution's PDF
        n = random.random()

        #Generate the inter-event time from the exponential distribution's CDF using the Inverse-CDF technique
        inter_event_time = -math.log(1.0 - n) / _lambda
        inter_event_times.append(inter_event_time)

    A = inter_event_times
    cumSum = [sum(A[:i+1]) for i in range(len(A))]
     # find what that is
    depart = [0]*len(A)
    depart[0] = cumSum[0]
    for i in range(1,len(A)):
        depart[i] = max(depart[i-1] + min_time_to_send, cumSum[i])
    diff_list = []
    for x, y in zip(depart[0::], depart[1::]):
        diff_list.append(y-x)
    A_new = [A[0]]+ diff_list
    cumSum2 = [sum(A_new[:i+1]) for i in range(len(A_new))]
    queue_times = [x-y for x,y in zip(cumSum2,cumSum) ]
    return A_new, queue_times



def main():
    global t0
    generating_times = {}
    t0 = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_addr', type=str, default='10.0.2.2',help="The destination IP address to use")
    parser.add_argument('--message', type=str, default='',help="The message to include in packet")
    parser.add_argument('--dst_id', type=int, default=None, help='The heartBeat dst_id to use, if unspecified then heartbeat header will not be included in packet')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    dst_id = args.dst_id
    iface = get_if()
    a_m_idx = [[0,2],[1,3],[2,0],[3,1],[2,3]]

    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_barebone = IP(dst=addr) / TCP(dport=1111, sport=50001) / args.message
            
    prev_dst_id = 1
    dst_id = 1
    acked_idx = 0
    sent_idx = 0
    mean_time = 0.1
    min_time_to_send = 0.05
    inter_times, queue_times = generate_traffic_model_M_D_1(mean_time, min_time_to_send)
    traffic_ind = 0
 	

    while True:
        f = open("/home/thanos/tutorials/exercises/p4_FWB/3gpp_dst_holder.txt", "r")
        line = f.read()
        dst_id = int(line.split()[0])
        acked_idx = int(line.split()[1])
        transitioning_time = float(line.split()[2])
        t0_listener = float(line.split()[3])
        f.close()
        if dst_id in a_m_idx[prev_dst_id]:
            prev_dst_id = dst_id
            generating_times[sent_idx] = time.time() - t0 + t0_listener - queue_times[sent_idx%len(queue_times)]
            pkt = e / fwb(dst_id=dst_id, pkt_id=sent_idx+1, pid=TYPE_IPV4) /  pkt_barebone / str(generating_times[sent_idx])
            sent_idx = sent_idx + 1
            time_to_send = inter_times[traffic_ind%len(inter_times)]
            sendp(pkt, inter=time_to_send, iface=iface, verbose=False)
            traffic_ind += 1
            #print(traffic_ind%len(traffic_model_rate))
			
        else:
            prev_dst_id = dst_id
            highest_buffered_idx = sent_idx - 1
            sent_idx = acked_idx - 1
            #t1 = time.time()
            #print('from:{}, to:{}'.format(sent_idx,highest_buffered_idx))
            for i in range(acked_idx+1,highest_buffered_idx+1):
	            print(sent_idx)
	            pkt = e / fwb(dst_id=dst_id, pkt_id=sent_idx+1, pid=TYPE_IPV4) /  pkt_barebone / str(generating_times[sent_idx])
	            sent_idx = sent_idx + 1
	            sendp(pkt, inter= min_time_to_send, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
