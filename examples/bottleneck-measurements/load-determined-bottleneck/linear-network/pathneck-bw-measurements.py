"""
An experiment where pathneck is used to both detect a bottleneck in a network
with linear topology and estimate the bandwidth on the bottleneck link.
"""
import subprocess
import os
import numpy as np
from setup import configure_link, read_state_json
import statistics
import matplotlib.pyplot as plt

bottleneck_link_dest = {'name': 'r3', 'ip': '10.0.3.3'}
bottleneck_link_name = "r2-r3"
server = {'name': 's1', 'ip': '10.0.5.5'}
contesting_client = 'c2'
client = 'c1'

n_iter = 10
latency_const = 1
burst_const = 12500

bottlneck_bw_values = list(np.arange(10, 101, 5))
print(bottlneck_bw_values)

# setup iperf server on bottleneck link destination
os.system(f"docker exec {bottleneck_link_dest['name']} iperf -s &")

# generate background traffic from c2 to r3 (through r2)
os.system(f"docker exec {contesting_client} iperf -t 0 -c {bottleneck_link_dest['ip']} &")

# run pathneck from client c1 to server s1
bandwidth_est = []
for i in range(len(bottlneck_bw_values)):
	# configure bandwidth on bottleneck link
	current_state = read_state_json()
	links = current_state["links"]
	tc_params = (bottlneck_bw_values[i], burst_const, latency_const)
	bottleneck_endpoint0 = links[bottleneck_link_name][1][0]
	bottleneck_endpoint1 = links[bottleneck_link_name][1][1]
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
plt.scatter(bottlneck_bw_values, bandwidth_est, c='orange')
plt.axline((0, 0), slope=1, c='black', linestyle='--')
plt.xlabel('Bandwidth values on bottleneck configured with tc')
plt.ylabel('Measured bandwidth on detected bottlneck with pathneck')
plt.title(f'Bandwidth [Mbits/sec] comparison')
plt.savefig('pathneck-bandwidth-measurements')
plt.show()

