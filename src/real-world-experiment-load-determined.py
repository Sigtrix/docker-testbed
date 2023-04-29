"""
An experiment where pathneck is used to both detect a bottleneck in a network
with linear topology and estimate the bandwidth on the bottleneck link.
"""
import subprocess
import os
import numpy as np
import statistics
import matplotlib.pyplot as plt
from src.setup import configure_link, read_state_json

bottleneck_link_dest = {'name': 'enb1', 'ip': '10.0.3.2'}
dynamic_link_name = "r1-enb2"
server = {'name': 'ue1', 'ip': '10.0.3.4'}
contesting_client = 'enb2'
client = 'ue4'

n_iter = 5
latency_const = 1
burst_const = 12500

# setup iperf server on server and bottleneck dest
os.system(f"docker exec {server['name']} iperf -s &")
os.system(f"docker exec {bottleneck_link_dest['name']} iperf -s &")

# generate background traffic on path from client to server
os.system(f"docker exec {client} iperf -t 0 -c {server['ip']} &")
# generate background traffic on bottleneck link from contesting client
os.system(f"docker exec {contesting_client} iperf -t 0 -w 1M -c {bottleneck_link_dest['ip']} &")

bottlneck_bw_values = list(np.arange(10, 60, 10))
n_streams = len(bottlneck_bw_values)
print(bottlneck_bw_values)

# run pathneck from client c1 to server s1
bandwidth_est = []
for i in range(n_streams):
	# configure link before bottleneck link
	contesting_traffic = bottlneck_bw_values[i]
	print(f"contesting traffic: {contesting_traffic}")
	current_state = read_state_json()
	links = current_state["links"]
	tc_params = (contesting_traffic, burst_const, latency_const)
	bottleneck_endpoint0 = links[dynamic_link_name][1][0]
	bottleneck_endpoint1 = links[dynamic_link_name][1][1]
	configure_link(bottleneck_endpoint0[0], bottleneck_endpoint0[2], tc_params)
	configure_link(bottleneck_endpoint1[0], bottleneck_endpoint1[2], tc_params)
	bottleneck_bandwidth = []
	for j in range(n_iter):
		result = subprocess.run(['docker', 'exec', client, './pathneck-1.3/pathneck', '-o', server['ip']], stdout=subprocess.PIPE)
		output = result.stdout.decode('utf-8')
		print(output)
		bottleneck = None
		for line in output.splitlines():
			line = line.split()
			if len(line) == 8:
				if line[5] == '1':
					bottleneck = line[0]
					bottleneck_bandwidth.append(float(line[6]))
	# calculate median estimated bandwidth
	bandwidth_est.append(statistics.median(bottleneck_bandwidth))

# plot bandwidth test results
plt.scatter(np.arange(1, n_streams+1), bandwidth_est, c='orange')
plt.xlabel('Number of parallel streams on bottleneck link')
plt.ylabel('Measured bandwidth on detected bottlneck with pathneck')
plt.title(f'Bandwidth [Mbits/sec] comparison')
plt.savefig('pathneck-bandwidth-measurements')
plt.show()
