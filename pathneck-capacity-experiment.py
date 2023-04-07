"""
An experiment measuring the gap values of hops for a linear network topology
with a capacity determined bottleneck
"""
import subprocess
import os
import re
import numpy as np
from setup import configure_link, read_state_json
import matplotlib.pyplot as plt

bottleneck_link_dest = {'name': 'r3', 'ip': '10.0.3.3'}
server = {'name': 's1', 'ip': '10.0.5.5'}
contesting_client = 'c2'
client = 'c1'

# setup iperf server on bottleneck link destination
os.system(f"docker exec {bottleneck_link_dest['name']} iperf -s &")

# generate background traffic from c2 to r3 (through r2)
os.system(f"docker exec {contesting_client} iperf -t 0 -c {bottleneck_link_dest['ip']} &")

# run pathneck from client c1 to server s1
result = subprocess.run(['docker', 'exec', client, './pathneck-1.3/pathneck', '-o', server['ip']], stdout=subprocess.PIPE)
output = result.stdout.decode('utf-8')
print(output)
hop_ids = []
gap_values = []
bottleneck = None
for line in output.splitlines():
	line = line.split()
	if len(line) == 8:
		hop_ids.append(line[0])
		gap_values.append(int(line[4]))
		if line[5] == '1':
			bottleneck = line[0]

# plot gap values results
plt.scatter(hop_ids, gap_values, c='orange')
plt.plot(hop_ids, gap_values, c='black')
if bottleneck is not None:
	plt.scatter(bottleneck, gap_values[hop_ids.index(bottleneck)], marker='x', s=100, c='black')
plt.xlabel('hop ID')
plt.ylabel('gap values [us]')
plt.title('gap values')
plt.savefig('gap-measurements')
plt.show()


