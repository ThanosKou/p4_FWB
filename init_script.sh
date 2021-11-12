h1 ./clear_dst.sh
h1 ./listen_and_update.py &
h3 ./BS1.py &
h4 ./BS2.py &
h1 ./3gpp_listen_and_update.py &
h2 ./v2_UE-listener.py &
h1 ./reader_sender.py &
h2.monitor()
