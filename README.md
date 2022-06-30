# Description

This implements the FWB logic in the network shown in simple_topology.jpg.

Specifically, Switch 1 (S1) plays the role of the FWB-GW. Switches 2 and 3 (S2 & S3 including their hosts h3 & h4, respectively) act as the primary and secondary BS of the UE, respectively. Switch 4 (S4) is a virtual switch and acts us a sink node for the UE.

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
To compile all the results into a dataframe and plot the results, simply change the data_path variable to point to your datafolder in python [script](https://github.com/ThanosKou/p4_FWB/blob/main/data_analysis/main.py) on lines 54-55 and uncomment. This will create the dataframe, and plot the packet arrival times.
Below is the results of our experiment.
>![Figure_1](https://github.com/ThanosKou/p4_FWB/blob/main/data_analysis/Figure_1_gw_only.png) **Figure 1:** Paket arrival times relative to the first packet arrival of the flow, i.e., first packet arrival time is shifted to zero. The gateway delay is a significant source of inter-packet latency which will jepoardize the quality of experience of low latency applications. Our proposed method hides the handover latency from the UE by prefetching packets to a secondary backup base station. The staircase behaivour in 3GPP is due to the additional latency introduced while fetching the packets from the GW during a handover event.
