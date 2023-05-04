# Testbed Setup
This directory consists of three scripts:
- [setup.py](setup.py)
- [experiment.py](experiment.py)
- [topology_config.py](topology_config.py)

Further information on how to define a topology
configuration and run a user defined experiment
can be found in the project root directory. Here
the focus will be on the underlying implementation
intended for those who want to expand upon the system:

1. The [setup](setup.py) script expects a [config file](topology_config.py)
specifying the nodes in the networks and their interconnections
in the format detailed in the [sample file](topology_config.py).
Given a config file in the expected format the setup script creates
Docker subnets for each link present in the network. Then it proceeds
by creating containers for each node in the network and attaches
containers to networks for each link connected to the corresponding
node. 
2. If a container is attached to more than one link it is
connected to each one on a unique interface which is automatically
assigned in increasing order based on the order of links for the
specific container in the config file.
3. When attaching containers to subnets the bandwidth and latency specfied
    in the config is also configured for the link. This is done by calling
   the relevant *tc qdisc* and *netem* commands.
4. When a unique container and subnet has been set up for every node and
   link in the config respectively, the setup proceeds by configuring the 
   routing tables on each container:
   1. To determine the routing in the network Dijkstra's algorithm is used with the cost set 
   to the multiplicative inverse of the bandwidth specified in the config.
   2. To set up the routing behaviour on the containers relevant *ip route*
   commands are run on each container.

After all these steps a network with nodes and interconnections
as specified in the config file has been set up and user defined
experiments can be run with the setup. Experiments are 
in the form of python scripts and a few examples are provided in the
[examples](../examples) directory that should help users getting
started defining their own experiments.


   
   
