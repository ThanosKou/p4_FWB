h1 ./3gpp_clear_dst.sh
h1 ./3gpp_listen_and_update.py &
h2 ./3gpp_UE-listener.py &
h1 ./3gpp_reader_sender.py &
h2.monitor()
