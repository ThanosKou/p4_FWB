h1 ./clear_dst.sh
#h1 ./listen_and_update.py &
h1 sudo tcpdump -i eth0 -w GW_packets.pcap &
h2 sudo tcpdump -i eth0 -w UE_packets.pcap &
h3 ./BS1.py &
h4 ./BS2.py &
xterm h2
xterm h1
