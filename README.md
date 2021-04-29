## Prerequisites 

In order for this to work, we need to have installed p4 and the related dependencies. If you haven't already installed p4, you can use the instructions in https://github.com/jafingerhut/p4-guide to do so.

After this is done, clone the present repo inside the folder tutorials/exercises that should have already been created.

## Run this exercise 
To compile the p4 program:

``` sudo make run ```


 This should open mininet. You can check connectivity by 
 
 ```pingall```
 
 For individual host and switch testing, you can use `xterm`. For example, to open terminals for hosts h1,h2 and switch s1: 
 
 ```xterm h1 h2 s1``` 
 
 To send a single packet you can use the scripts `send.py` and `receive.py`. For exmaple, if you want to send a single packet that contains the message "hello" from h1 to h2, do `./receive.py` at h2's terminal (you can sniff the incoming packets) and at h1's terminal do:
 
 ```./send.py 10.0.1.1 "hello" ```
 
 Moreover, if you want to send a packet that contains a **heartbeat header**, at h1's terminal do isntead:
 
  ```./send.py 10.0.1.1 "hello" --dst_id 1```
