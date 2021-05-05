## Description

This implements the FWB logic in the network shown in simple_topology.jpg.

Specifically, Switch 1 (S1) plays the role of the FWB-GW. Switches 2 and 3 (S2 & S3) act as the primary and secondary BS of the UE, respectively. Switch 4 is a virtual switch and acts us a sink node for the UE.

## Prerequisites 

In order for this to work, we need to have p4 installed  and the related dependencies. If you haven't already installed p4, you can use the instructions in https://github.com/jafingerhut/p4-guide to do so.

After this is done, clone the present repo inside the folder tutorials/exercises that should have already been created.

## Run this exercise 
To compile the p4 program:

``` make stop ```
``` sudo make run ```


 This should open mininet. You can check connectivity by 
 
 ```pingall```
 
 For individual host and switch testing, you can use `xterm`. For example, to open terminals for hosts h1,h2 and switch s1: 
 
 ```xterm h1 h2 s1``` 
 
 To send a single packet you can use the scripts `send.py` and `receive.py`. For exmaple, if you want to send a single packet that contains the message "hello" from h1 to h2, do `./receive.py` at h2's terminal (you can sniff the incoming packets) and at h1's terminal do:
 
 ```./send.py 10.0.1.1 "hello" ```
 
 To run `send.py` and `receive.py`, you may need to do `chmod u+x send.py receive.py` beforehand.
 
The FWB operation is done by default. By specifying the dst_id in the packet that you send via `send.py` you can change the packet route. Specifically,

```dst_id = 0 => multicast (BS1 is primary, S3 is secondary)```

```dst_id = 1 => S2 is primary, S3-UE link is down```

```dst_id = 2 => S3 is primary, S2-UE link is down```

```dst_id = 3 => both S2-UE and S3-UE links are down```

To test `dst_id` utility in the network, in h1's xterm do:

 ```./send.py 10.0.1.1 "hello" --dst_id %x```
 
 , where `%x` is the desired dst_id.
 
 For now, the buffering utlity at the secondary BS is simply dropping the received packets. Will update soon. 
