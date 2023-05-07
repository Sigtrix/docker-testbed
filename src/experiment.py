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
import csv
import time

bottleneck_link_dest = {'name': 'r5', 'ip': '10.0.3.4'}
server = {'name': 's1', 'ip': '10.0.4.4'}
contesting_client = 'c2'
client = 'c1'
bottleneck_link_name = 'c2-r4'

latency_const = 1
burst_const = 12500
n_iter = 20
bottleneck_bandwidth = []
data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}
bottlneck_bw_values = list(np.arange(10, 101, 10))
print(bottlneck_bw_values)

os.system(f"docker exec {contesting_client} pkill iperf")
os.system(f"docker exec {client} pkill iperf")
os.system(f"docker exec {server['name']} pkill iperf")
os.system(f"docker exec {bottleneck_link_dest['name']} pkill iperf")
# setup iperf server on server
os.system(f"docker exec {server['name']} iperf -s &")
os.system(f"docker exec {bottleneck_link_dest['name']} iperf -s &")

# generate background traffic on path from client to server
os.system(f"docker exec {client} iperf -t 0 -c {server['ip']} &")
# os.system(f"docker exec {contesting_client} iperf -t 0 -c {bottleneck_link_dest['ip']} &")

# run pathneck from client c1 to server s1
bandwidth_est = []
confidence_level_list = []
test_results = []
for i in range(len(bottlneck_bw_values)):
	# configure bandwidth on bottleneck link
	current_state = read_state_json()
	links = current_state["links"]
	tc_params = (bottlneck_bw_values[i], burst_const, latency_const)
	bottleneck_endpoint0 = links[bottleneck_link_name][1][0]
	bottleneck_endpoint1 = links[bottleneck_link_name][1][1]
	configure_link(bottleneck_endpoint0[0], bottleneck_endpoint0[2], tc_params)
	configure_link(bottleneck_endpoint1[0], bottleneck_endpoint1[2], tc_params)
	print(f"Bandwidth value = {bottlneck_bw_values[i]}")
	result = os.popen(f"docker exec {contesting_client} iperf -t 20 -c {bottleneck_link_dest['ip']}").read()
	lines = result.splitlines()
	line = lines[6].split()
	bandwidth_est.append(line[6])
	os.system(f"docker exec {contesting_client} pkill iperf")
	time.sleep(2)
	
# plot bandwidth test results
plt.scatter(bottlneck_bw_values, bandwidth_est, c='orange')
plt.xlabel('Bandwidth values configured with tc')
plt.ylabel('Measured bandwidth on contending link with iperf')
plt.title(f'Bandwidth [Mbits/sec] comparison')
plt.savefig('iperf-bandwidth-measurements')
plt.show()

os.system(f"docker exec {contesting_client} pkill iperf")
os.system(f"docker exec {client} pkill iperf")
os.system(f"docker exec {server['name']} pkill iperf")
os.system(f"docker exec {bottleneck_link_dest['name']} pkill iperf")