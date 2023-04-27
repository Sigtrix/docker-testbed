"""
An experiment where pathneck is used to both detect a bottleneck in a network
with linear topology and estimate the bandwidth on the bottleneck link.
"""
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(os.path.dirname(current))
sys.path.append(parent)
import subprocess
import os
import numpy as np
from src.setup import configure_link, read_state_json
import statistics
import matplotlib.pyplot as plt
import csv

bottleneck_link_dest = {'name': 'enb1', 'ip': '10.0.3.2'}
bottleneck_link_name = "r1-enb1"
server = {'name': 'ue1', 'ip': '10.0.3.4'}
client = 'extra'

n_iter = 5
latency_const = 1
burst_const = 12500

bottlneck_bw_values = list(np.arange(10, 101, 10))
print(bottlneck_bw_values)

# setup iperf server on server
os.system(f"docker exec {server['name']} iperf -s &")

# generate background traffic on path from client to server
os.system(f"docker exec {client} iperf -t 0 -c {server['ip']} &")

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
	bottleneck_bandwidth = []
	confidence_level = []
	print(f"Bandwidth value = {bottlneck_bw_values[i]}")
	for j in range(n_iter):
		result = subprocess.run(['docker', 'exec', client, './pathneck-1.3/pathneck', '-o', server['ip']], stdout=subprocess.PIPE)
		output = result.stdout.decode('utf-8')
		print(output)
		bottleneck = None
		bottleneck_bw = None
		conf_level = None
		for line in output.splitlines():
			line = line.split()
			if len(line) == 8:
				if line[5] == '1':
					bottleneck = line[0]
					bottleneck_bw = float(line[6])
					bottleneck_bandwidth.append(float(line[6]))
			if len(line)>= 3 and line[0] == 'conf':
				confidence_level.append(float(line[2]))
				conf_level = float(line[2])
				print(f"Conf level = {conf_level}")
		test_results.append([bottlneck_bw_values[i], j, bottleneck, bottleneck_bw, conf_level])
	# calculate median estimated bandwidth
	bandwidth_est.append(statistics.median(bottleneck_bandwidth))

# save test results to CSV file
with open('test_results.csv', mode='w', newline='') as csv_file:
    fieldnames = ['Bandwidth', 'Iteration', 'Bottleneck', 'Bottleneck_BW', 'Conf_Level']
    writer = csv.writer(csv_file)
    writer.writerow(fieldnames)
    for result in test_results:
        writer.writerow(result)
	
# plot bandwidth test results
plt.scatter(bottlneck_bw_values, bandwidth_est, c='orange')
plt.axline((0, 0), slope=1, c='black', linestyle='--')
plt.xlabel('Bandwidth values configured with tc')
plt.ylabel('Measured bandwidth on detected bottlneck with pathneck')
plt.title(f'Bandwidth [Mbits/sec] comparison')
plt.savefig('pathneck-bandwidth-measurements')
plt.show()
