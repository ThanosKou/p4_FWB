# Description

This implements the FWB logic in the network shown in simple_topology.jpg.

Specifically, Switch 1 (S1) plays the role of the FWB-GW. Switches 2 and 3 (S2 & S3 including their hosts h3 & h4, respectively) act as the primary and secondary BS of the UE, respectively. Switch 4 (S4) is a virtual switch and acts us a sink node for the UE.

Next, we will describe the role of each node in our FWB network emulation. 
## 5G-CN 
The downlink packet is generated here along with the FWB header. For the FWB header, the Protocol ID is always 0x800 indicating that the next header is IP. The Pckt ID is set as 1 for the first packet of every new UE-specific flow, and it is increased by 1 every time a downlink packet for that UE is generated. The Dst ID is originally set as 0, which indicates normal FWB operation: BS1 is the master gNB-DU, and BS2 is the secondary gNB-DU. The 5G-CN node will keep using the same Dst ID, until it receives an FWB control packet from the UE, which carries a different Dst ID. As soon as the 5G-CN receives the control packet, it will use the new Dst ID for downlink traffic.

## FWB-GW
The FWB-GW is the first P4switch that a downlink packet reaches after it leaves the 5G-CN. The FWB-GW inspects the packet header and based on the destination IP and the FWB Dst ID, it performs an action. The possible actions in the FWB-GW node are:
```
 * multicast: this action is performed if the UE is connected to both gNBs, i.e., if Dst ID is 0 or 1. In this case, the FWB-GW multicasts the downlink packet to both gNBs. 
 * forwarding: this action is performed if the UE is connected to only one gNB, i.e., if Dst ID is 2 or 3. In this case, the FWB-GW will only forward to the serving gNB. 
 * drop: this action is performed if the UE is out-of-service.
```    
Note that in our simulation, we have simplified the operation of the FWB-GW. Normally, the FWB-GW contains the routing related information. However, for simplicity we have assigned this responsibility to the 5G-CN node, as in our mininet topology 

## Base Station (BS)
In our emulation, the gNBs of the FWB network are also P4 switches. Similar to the FWB-GW, when a BS receives a downlink packet, it parses its header, and based on the destination IP and the FWB Dst ID, it performs an action. The possible actions in the gNB-DU node are:
```
  * forwarding: this action is performed if this is the master gNB of the UE, which is indicated by the FWB Dst ID. In this case, the BS forwards the packet to the UE.
  * buffer: this action is performed if the gNB is the secondary gNB-DU of the UE, which is also indicated by the FWB Dst ID. In this case, the gNB-DU stores the downlink packet to its downlink buffer. The buffer implementation is described in the following subsection. 
  * drop: this action is performed if the gNB does not serve the UE.
```

## Buffer
In our simulation, each gNB node has a downlink buffer, which is implemented by a corresponding host in our mininet topology. After a successful buffer match-action, the secondary gNB forwards the packet to the buffer node. A downlink packet remains at the buffer until either it becomes the oldest packet and there is no extra buffer space or the gNB is assigned to be the master gNB-DU for the specific UE. The master gNB assignment occurs through an FWB control packet. The FWB control packet also contains a Pckt ID, which is the sequence number of the next packet that the UE requires to be transmitted. The buffer node will then forward this packet and all packets with a sequence number higher than the Pckt ID to the UE. At the same time, the buffer node forwards the FWB control packet to its upstream, so that it reaches the 5G-CN node and the FWB header of the downlink traffic is updated.

## UE
The UE is implemented as a mininet host and apart from receiving downlink traffic, it is responsible for notifying the rest of the FWB network about link changes. Specifically, at the times when a serving BS gets blocked, the UE sends FWB control packets that contain a) a Dst ID indicating the multicast tree update and b) a Pckt ID corresponding to the last successfully received packet. Recall that, the serving gNB will then forward this FWB control packet to its buffer node, which will immediately send all packets with a sequence number equal or higher than the Pckt ID. At the same time, the buffer node will forward the FWB control packet to its upstream, so that it reaches the 5G-CN node and FWB header of the downlink traffic is updated.

## Modified Packet 

In the FWB proof-of-concept implementation, the packet header includes the FWB header, which contains three fields: the Protocol ID, the Destination ID (Dst ID), and the Packet ID (Pckt ID). The Protocol ID is used to identify the type of the next header, which in this case is the IP header. The Dst ID provides routing information: it indicates which gNBs belong to the UE multicast tree, as well as which gNB is master. For our network example, the mapping between Dst ID and the corresponding routing is shown [here](https://github.com/ThanosKou/p4_FWB/blob/d1189f45199cf13548ae45ae1fe3568f885b9130/destinationID_mapping.png). The Pckt ID field contains a sequence number for the current packet. The `P4` switches can parse and process these customized packets according to rules that are generated in the network setup. 


# Prerequisites 

In order for this to work, we need to have p4 installed  and the related dependencies. If you haven't already installed p4, you can use the instructions in https://github.com/jafingerhut/p4-guide to do so.

We provide an installation script `install-p4dev-v2.sh`, edited version of the script given in [jafingerhut/p4-guide](https://github.com/jafingerhut/p4-guide). The changes we make specifically for improving the speed of the behavioral-model of p4 as well as the specific core inputs for our 8 core cpu computer. We run our experiments on Ubutunu 18.04 running on a laptop equipped with intel i7 6700 cpu. We can get about 1Gbps speeds using the stress test script given in [p4lang /
behavioral-model](https://github.com/p4lang/behavioral-model/tree/main/mininet) repository.

After this is done, clone [our repository](https://github.com/ThanosKou/p4_FWB) inside the folder tutorials/exercises that should have already been created.

```
cd ~/tutorials/exercises
git clone https://github.com/ThanosKou/p4_FWB
```

If you are not interested in bmv2 performance but just want to run the experiment the easiest way would be using the VM image provided in [p4lang/tutorials](https://github.com/p4lang/tutorials), following their instructions.


# Run this exercise 
We provide a mininet [bootstrap script](https://github.com/ThanosKou/p4_FWB/blob/main/init_script.sh) that runs the programs, the BS logic, GW logic and UE logic, in their respective hosts. Moreover this bootstrap creates the mininet topology, applies the forwarding rules to our p4 switches.
To run a specific delay scenario change links at the [topology](https://github.com/ThanosKou/p4_FWB/blob/main/pod-topo/topology.json) file, and edit the latencies, in ms units.

We also need to change the script for running the experiment to apply our bootstrap script to mininet at the start. This script is provided in the [p4lang/tutorials](https://github.com/p4lang/tutorials) repository. We change the file with our [edited experiment script](https://github.com/ThanosKou/p4_FWB/blob/main/run_exercise.py).
```
cp ./run_exercise.py ../../utils/run_exercise.py
```

We also provided a init script for 3GPP, to run 3GPP scenario simply change the lines 358 and 359 at this script. (uncomment and comment).


## Running the experiments
Now that we cleared all the prerequisites, dependencies and folder setup, we can run our first experiment.
First, adjust the link delays (if you need to) by modifying the [topology file](https://github.com/ThanosKou/p4_FWB/blob/main/pod-topo/topology.json).
Then, run the experiment for the FWB architecture:
```
./prep_FWB.sh
sudo make run
```
This will start the mininet topology and start the processes on the hosts. The UE then will record each packet arrival time to the [data folder](https://github.com/ThanosKou/p4_FWB/tree/main/out_data).

To run the experiment for the 3GPP architecture:
```
./prep_3GPP.sh
sudo make run
```
# Results
To compile all the results into a dataframe and plot the results, simply change the data_path variable to point to your datafolder in python [script](https://github.com/ThanosKou/p4_FWB/blob/main/data_analysis/main.py) on lines 54-55 and uncomment. This will create the dataframe, and plot the cdf of packet delay.
