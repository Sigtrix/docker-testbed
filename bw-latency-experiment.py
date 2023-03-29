"""
An experiment 1) comparing measured bandwidth using iperf with
bandwidth configured with tc tbf and 2) comparing measured latency using ping with
latency configured with tc tbf. This experiment can be run
on an existing topology.
"""
import subprocess
import os
import numpy as np
import re
from config import links
from setup import configure_link, read_state_json
import matplotlib.pyplot as plt


server = {'name': 's1', 'ip': '10.0.3.4'}
client = 'c1'

bandwidth_values = [1, 2, 4, 8, 16, 32, 64, 128]
bandwidth_results = []

num_links = 6  # number of links on path to and from client and server
latency_values = list(np.arange(1, 20, 1)) + list(np.arange(20, 110, 10))
latency_results = []


def configure_params(links, params):
	"""
	Configure links in network with same params
	:param links: links in the current state
	:param params: tuple (bandwidth, burst, latency)
	:return: None
	"""
	for link_name, link_param in links.items():
		endpoint0 = link_param[1][0]
		endpoint1 = link_param[1][1]
		configure_link(endpoint0[0], endpoint0[2], params)
		configure_link(endpoint1[0], endpoint1[2], params)


# setup iperf server on s1
os.system(f"docker exec {server['name']} iperf -s &")

for i in range(len(bandwidth_values)):
	# update bw on all links
	tc_params = (bandwidth_values[i], 2, 2)
	print(tc_params)
	current_state = read_state_json()
	links = current_state["links"]
	configure_params(links, tc_params)

	result = subprocess.run(['docker', 'exec', client, 'iperf', '-c', server['ip']], stdout=subprocess.PIPE)
	output = result.stdout.decode('utf-8')
	print(output)

	# parse output to get bandwidth
	unit = output.split(' ')[-1]
	bandwidth = float(output.split(' ')[-2])
	if 'Kbits' in unit:
		bandwidth /= 1000
	bandwidth_results.append(bandwidth)


for i in range(len(latency_values)):
	# update latency on all links
	tc_params = (2, 2, latency_values[i])
	print(tc_params)
	current_state = read_state_json()
	links = current_state["links"]
	configure_params(links, tc_params)

	result = subprocess.run(['docker', 'exec', client, 'ping', '-c', '10', server['ip']], stdout=subprocess.PIPE)
	output = result.stdout.decode('utf-8')
	print(output)

	# parse output to get bandwidth
	output = re.split('[ /]', output)
	avg_latency = float(output[-4])
	avg_link_latency = avg_latency/num_links
	latency_results.append(avg_link_latency)


# plot bandwidth test results
plt.plot(bandwidth_values, bandwidth_results)
plt.xlabel('Bandwidth values configured with tc')
plt.ylabel('Measured bandwidth using iperf')
plt.title('Bandwidth comparison')
plt.savefig('bandwidth-measurements')
plt.show()

# plot latency results
plt.plot(latency_values, latency_results)
plt.xlabel('Latency values configured with tc')
plt.ylabel('Measured latency using ping')
plt.title('Latency comparison')
plt.savefig('latency-measurements')
plt.show()




