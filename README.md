# Docker Telemetry Testbed
This project provides a framework to set up arbitrary network topologies of
Docker containers and run user defined experiments for data collection on these networks.

## Requirements

- Docker (tested on 20.10.23)

## Usage

### Define a network topology
A network topology can be configured in a python file. Some examples
can be found in the [examples](file://examples)
folder. 

### Create network
To create a network of Docker containers from a network topology
configuration file, provide the config file as an argument to the
make command as follows:
```
make setup CONFIG=<file_path>
```

### Create an experiment
An experiment can be implemented as a python script. Some examples
can be found in the [examples](file:///examples)
folder. The default image supports among other tools: 
*ping*, *iperf*, *traceroute* and *pathneck*. If further tools
are needed for an experiment these can be added to the 
[Dockerfile](file:///Dockerfile).

### Run experiment
To run an experiment simply run the python script that defines
the experiment on the system with Docker installed and running.
The following make command can also be run:
```
make run EXPERIMENT=<file_path> 
```

*Note*: 
- To clean up resources after running an experiment simply run
the following make command:
```
make clean
```
- To set up a topology with from a topology config file <topology_config>
and run an experiment defined in a file <experiment_config> as well as
clean up resources after the experiment run the following make command:
```
make all CONFIG=<file_path> EXPERIMENT=<file_path>
```