"""
An experiment comparing measured bandwidth using iperf with
bandwidth configured with tc tbf. This experiment can be run
on an existing topology.
"""
import subprocess
import os
import re
from config import links
from setup import configure_link
import matplotlib.pyplot as plt


server = {'name': 's1', 'ip': '10.0.3.4'}
client = 'c1'
bandwidth_values = [2, 4, 8, 16, 32, 64, 128]
bandwidth_results = []


def configure_bandwidth(params):
	"""
	Configure links in network with same params
	:param params: tuple (bandwidth, burst, latency)
	:return: None
	"""
	for link_name, link_param in links.items():
		endpoint0 = link_param[1][0]
		endpoint1 = link_param[1][1]
		configure_link(endpoint0[0], endpoint0[2], params)
		configure_link(endpoint1[0], endpoint1[2], params)


# setup iperf server on s1
os.system(f"docker exec {server['name']} iperf -s")

# setup iperf client on c1 and collect results
result = subprocess.run(['docker', 'exec', client, 'iperf', '-c', server['ip']], stdout=subprocess.PIPE)
output = result.stdout.decode('utf-8')
print(output)

# parse output to get bandwidth
unit = output.split(' ')[-1]
bandwidth = float(output.split(' ')[-2])
if 'Kbits' in unit:
	bandwidth /= 1000
bandwidth_results.append(bandwidth)


for i in range(len(bandwidth_values)):
	# update bw on all links
	tc_params = (bandwidth_values[i], 2, 10)
	configure_bandwidth(tc_params)

	result = subprocess.run(['docker', 'exec', client, 'iperf', '-c', server['ip']], stdout=subprocess.PIPE)
	output = result.stdout.decode('utf-8')
	print(output)

	# parse output to get bandwidth
	unit = output.split(' ')[-1]
	bandwidth = float(output.split(' ')[-2])
	if 'Kbits' in unit:
		bandwidth /= 1000
	bandwidth_results.append(bandwidth)


# plot results
bandwidth_values = [1] + bandwidth_values
plt.plot(bandwidth_values, bandwidth_results)
plt.xlabel('Bandwidth values configured with tc')
plt.ylabel('Measured bandwidth using iperf')
plt.title('Bandwidth comparison')
plt.savefig('bandwidth-measurements')
plt.show()




