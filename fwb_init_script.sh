h1 ./fwb_clear_dst.sh
h1 ./fwb_listen_and_update.py &
h3 ./BS1.py &
h4 ./BS2.py &
h2 ./fwb_UE-listener.py &
h2 tcpdump -i eth0 -w UE_packets.pcap &
h1 tcpdump -i eth0 -w CN_packets.pcap &
h1 ./fwb_reader_sender.py &

h2.monitor()