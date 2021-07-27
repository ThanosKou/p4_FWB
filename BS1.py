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
import Queue as queue

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



def BS_1_dst_id_map(dst_id):
    my_role = 'nothing'
    if dst_id == 0:
        my_role = 'primary'
    elif dst_id == 1:
        my_role = 'secondary'
    elif dst_id == 2:
        my_role = 'primary'
    return my_role


def buffer_pkt_fwd(buffer_pkt):
    global current_dst_id
    fwd_pkt = buffer_pkt
    fwd_pkt[fwb].dst_id = current_dst_id # I was secondary now i am primary
    fwd_pkt[IP].src = '10.0.3.3'
    return fwd_pkt
   

def buffer_pkt_extract(my_buffer,ue_asks):
    global iface
    global current_dst_id 
    print(my_buffer)
    buffer_elem = [i for i in my_buffer if i != 0]
    to_send = [[pkt_id,gener_time] for [pkt_id,gener_time] in buffer_elem if pkt_id >= ue_asks]
    for pkt_id,gener_time in sorted(to_send):
        buff_pkt = e / fwb(dst_id=current_dst_id, pkt_id=pkt_id, pid=TYPE_IPV4)/ pkt_barebone / gener_time
	#buff_pkt.show()
        sendp(buff_pkt, iface=iface, verbose=False)




def handle_pkt(pkt):
    global iface
    global current_state
    global isTransition
    global my_buffer
    global w_idx
    global BUFFER_LEN
    global current_dst_id
    if fwb in pkt:
        if pkt[IP].src == '10.0.2.2' and pkt[TCP].dport==2222: #control packet
            # print('UE is asking for packets')
            # pkt.show()
            # print(my_buffer[w_idx-1])
            # send the next packets to UE
            isTransition = True
            current_dst_id = pkt[fwb].dst_id
            ue_asks = pkt[fwb].pkt_id
            buffer_pkt_extract(my_buffer,ue_asks)
            # notify the core w listen and update mechanism
            notification_pkt = e / fwb(dst_id=pkt[fwb].dst_id,pkt_id=0,
                pid=TYPE_IPV4)/IP(dst='10.0.1.1')/ TCP(dport=2222, sport=50003) / 'Notifying h1 (GW), BS1 is primary now Changed at packet idx {}'.format(ue_asks)
            sendp(notification_pkt,iface=iface,verbose=False)
            # notification_pkt.show()
        elif pkt[IP].src =='10.0.1.1' and pkt[TCP].dport==1111: #received data packet
            current_state = BS_1_dst_id_map(pkt[fwb].dst_id)
	    current_state == 'secondary'
            if current_state == 'secondary':
            	pkt_idx = pkt[fwb].pkt_id
            	my_buffer[w_idx] = [pkt_idx,str(bytes(pkt[TCP].payload))]
            	w_idx = (w_idx+1)%BUFFER_LEN
            	if isTransition:
                    fwd_pkt = buffer_pkt_fwd(pkt)
                    # fwd_pkt.show()
                    current_state = 'primary'
                    #send whatever i received in my buffer to UE:
                    sendp(fwd_pkt,inter = 0.1,iface=iface,verbose=False)
                    #fwd_pkt.show()
                # print(my_buffer[w_idx-1])
            #else:
            #    pkt.show()
            #    print(current_state)
            #    print('Somehting is wrong we shouldnt reach here')
        elif pkt[IP].src=='10.0.1.1' and pkt[TCP].dport==2222: #control packet
            isTransition = False
            current_dst_id = pkt[fwb].dst_id

        # f = open("/home/thanos/tutorials/exercises/p4_FWB/dst_holder.txt", "w")

        # f.write(str(pkt[fwb].dst_id))
        # f.close()
        # return pkt[fwb].dst_id]


def main():
    global iface
    ifaces = filter(lambda i: 'eth0' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "base station: using %s" % iface
    global e
    global last_received
    global pkt_barebone
    global current_dst_id
    current_dst_id = 1 
    e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=TYPE_FWB)
    pkt_barebone =  IP(dst='10.0.2.2') / TCP(dport=1111, sport=50003) / ''
    global BUFFER_LEN
    global my_buffer
    global w_idx
    global current_state
    global isTransition
    isTransition = False
    BUFFER_LEN = 1000
    my_buffer = [0]*BUFFER_LEN
    w_idx = 0
    prev_state = 'secondary'
    current_state = 'secondary'
    prev_destination = -1
    received_packet = sniff(iface = iface,  prn = lambda x : handle_pkt(x))


#     # current_dst_id = 0
#     # acked_idx = 0
#     # sent_idx = 0
#     # pkt = IP(dst=addr) / TCP(dport=1234, sport=51995) / args.message
#     # while True:       
#     #     while current_sent < current_acked + 100:
#     #         # send a packet setting the pkt index sent+1 number of packets here using current_dst_id
#     #         e =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
#     #         pkt = e / fwb(dst_id=dst_id, pkt_id=sent_idx+1) /  pkt
#     #         sendp(pkt, iface=iface, verbose=False)
#     #         sent_idx = sent_idx + 1
#     #         sleep(0.001)
#     #         # acked_idx = sniff(iface = iface, prn = lambda x: handle_pkt(x))
#     #     acked_idx = sniff(iface = iface, prn = lambda x: handle_pkt(x))



if __name__ == '__main__':
    main()
