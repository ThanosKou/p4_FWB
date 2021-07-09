h1 ./clear_dst.sh
h1 ./listen_and_update.py &
h3 ./BS1.py &
h4 ./BS2.py &
h2 tcpdump -i eth0 -w UE_packets.pcap &
xterm h2
xterm h1
