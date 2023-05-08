"""
An experiment 1) comparing measured bandwidth using iperf with
bandwidth configured with tc tbf and 2) comparing measured latency using ping with
latency configured with tc tbf. This experiment can be run
on an existing topology.
"""
import subprocess
import os
import re
import numpy as np
from setup import configure_link, read_state_json
import matplotlib.pyplot as plt
import importlib


server = 's1'
client = 'ue1'

bandwidth_values = list(np.arange(1, 101, 20))
bandwidth_results = []
latency_const = 1
burst_const = 12500

latency_values = list(np.arange(1, 20, 5))
latency_results = []
bandwidth_const = 2

config = importlib.import_module('dumbbell')
server_ip = 0
client_ip = 0
for node_name, node_param in config.nodes.items():
	if(node_name == server):
		server_ip = node_param[0]
	if(node_name == client):
		client_ip = node_param[0]


def configure_params(links, params):
	"""
	Configure links in network with same params
	:param links: links in the current state
	:param params: tuple (bandwidth, burst, latency)
	:return: None
	"""
	for _, link_param in links.items():
		endpoint0 = link_param[1][0]
		endpoint1 = link_param[1][1]
		configure_link(endpoint0[0], endpoint0[2], params)
		configure_link(endpoint1[0], endpoint1[2], params)


# setup iperf server on server node(destination node)
os.system(f"docker exec {server} iperf -s &")

for i in range(len(bandwidth_values)):
	# update bw on all links
	tc_params = (bandwidth_values[i], burst_const, latency_const)
	print(tc_params)
	current_state = read_state_json()
	links = current_state["links"]
	configure_params(links, tc_params)

	result = subprocess.run(['docker', 'exec', client, 'iperf', '-c', server_ip], stdout=subprocess.PIPE)
	output = result.stdout.decode('utf-8')
	print(output)

	# parse output to get bandwidth
	unit = output.split(' ')[-1]
	bandwidth = float(output.split(' ')[-2])
	if 'Kbits' in unit:
		bandwidth /= 1000
	elif 'Gbits' in unit:
		bandwidth *= 1000
	bandwidth_results.append(bandwidth)

# plot bandwidth test results
plt.scatter(bandwidth_values, bandwidth_results, c='orange')
plt.axline((0, 0), slope=1, c='black', linestyle='--')
plt.xlabel('Bandwidth values configured with tc')
plt.ylabel('Measured bandwidth using iperf')
plt.title(f'Bandwidth [Mbits/sec] comparison (latency {latency_const}ms)')
plotname = str(server) + "_" + str(client) + "bandwidth-measurements"
plt.savefig(plotname)
plt.show()


for i in range(len(latency_values)):
	# update latency on all links
	tc_params = (bandwidth_const, burst_const, latency_values[i])
	print(tc_params)
	current_state = read_state_json()
	links = current_state["links"]
	configure_params(links, tc_params)

	result = subprocess.run(['docker', 'exec', client, 'ping', '-c', '10', server_ip], stdout=subprocess.PIPE)
	output = result.stdout.decode('utf-8')
	print(output)

	# parse output to get bandwidth
	output = re.split('[ /]', output)
	avg_latency = float(output[-4])/2
	latency_results.append(avg_latency)

# plot latency results
plt.scatter(latency_values, latency_results, c='orange')
plt.axline((0, 0), slope=1, c='black', linestyle='--')
plt.xlabel('Latency values configured with tc')
plt.ylabel('Measured latency using ping')
plt.title('Latency comparison [ms]')
plotname = str(server) + "_" + str(client) + "latency-measurements"
plt.savefig(plotname)
plt.show()




