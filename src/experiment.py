"""
An experiment measuring the gap values of hops for a linear network topology
with a capacity determined bottleneck
"""
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append('..')
from utils.experiment_helpers import iperf_server, iperf_client, pathneck, parse_pathneck_result, capture_traffic

# global variables
n_iter = 20
bottleneck_bandwidth = []
data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}

server = {'name': 's1', 'ip': '10.0.4.4'}
contesting_client = 'c2'
client = 'c1'
bottleneck_link_dest = {'name': 'r6', 'ip': '10.0.8.4'}
bottleneck_router = 'r5'

# setup iperf server on bottleneck link destination
iperf_server(server['name'])
iperf_server(bottleneck_link_dest['name'])

# generate background traffic
iperf_client(client, server['ip'])
iperf_client(contesting_client, bottleneck_link_dest['ip'])

# capture traffic on bottleneck router
capture_traffic(bottleneck_router, 'eth1', '180', 'traffic-capture')

# run pathneck from client to server
for i in range(n_iter):
	result = pathneck(client, server['ip'])
	print(result)
	bottleneck, bottleneck_bw = parse_pathneck_result(result)
	bottleneck_bandwidth.append(bottleneck_bw)
	data[bottleneck].append(bottleneck_bw)

# plot bandwidth test results
total_data = [data[key] for key in data]
sns.stripplot(data=total_data, jitter=True, color='black')
sns.boxplot(total_data)
plt.xlabel('Hop ID')
plt.ylabel('Measured bandwidth ')
plt.title(f'Bandwidth [Mbits/sec] distributions of detected bottlenecks')
plt.savefig('pathneck-boxplot')
plt.show()

os.system(f"docker exec {contesting_client} pkill iperf")
os.system(f"docker exec {client} pkill iperf")
os.system(f"docker exec {server['name']} pkill iperf")
os.system(f"docker exec {bottleneck_link_dest['name']} pkill iperf")
