# Docker Telemetry Testbed
This project provides a framework to set up arbitrary network topologies of
Docker containers and run user defined experiments for data collection on these networks.

## Requirements

- Docker (tested on 20.10.23)

## Usage

### Define a network topology
A network topology can be configured in a python file. Some examples
can be found in the [examples](examples)
folder. 
In order to make your own custom network topology the following information can be helpful:
In the configuration file only include those nodes which have atleast connection with any other node.
While defining the nodes, the node_name, ip_address of the node connected to base link and the base link name has to be provided. Ensure that the ip address of both the nodes sharing the base link have the ip address in the same subnet. 
Use a subnet mask of 255.255.255.0 to create a new subnet. Each base link should have a separate subnet. The exact IP
address of the node can be defined as any unique and valid IP address of the subnet being used by it's base link.
A node may be involved in two or more base links but while defining the node, include only one base link.
Define nodes using the following format: 
nodes = {node_name: (ip_addr, base_link_name), node2_name: (ip_addr2, base_link_name2), ...}

Define the links using the following format:
[((endpoint_name1, ip1), (endpoint_name2, ip2), (bandwidth[Mbit/s], burst[kb], latency[ms])), ...]
Our code automatically generates the link with the link name endpoint_name1-endpoint_name2 with the IP subnet to which 
the ips of both the node belong to. Thus ensure that the order you include the node information in the definition of 
the link corresponds to the intended link name.

### Create network
To create a network of Docker containers from a network topology
configuration file, provide the config file as an argument to the
make command as follows:
```
make setup CONFIG=<file_path>
```

### Create an experiment
An experiment can be implemented as a python script. Some examples
can be found in the [examples](examples)
folder. The default image supports among other tools: 
*ping*, *iperf*, *traceroute* and *pathneck*. If further tools
are needed for an experiment these can be added to the 
[Dockerfile](Dockerfile).

### Run experiment
To run an experiment simply run the python script that defines
the experiment on the system with Docker installed and running.
The following make command can also be run:
```
make run EXPERIMENT=<file_path> 
```
For running any test scripts on the data generated from the experiment,
run the following command.
```
make test TESTSCRIPT=<file_path>

*Note*: 
- To clean up resources after running an experiment simply run
the following make command:
```
make clean
```
Note that the make clean uses the state.json file which is present in the tmp directory.
Hence, if the state.json gets deleted or updated not by the current run, then the docker resources
need to be manually cleaned.

- To set up a topology with from a topology config file <topology_config>
and run an experiment defined in a file <experiment_config> as well as
clean up resources after the experiment run the following make command:
```
make all CONFIG=<file_path> EXPERIMENT=<file_path>
```