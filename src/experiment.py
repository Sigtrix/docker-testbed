"""
An experiment measuring the gap values of hops for a linear network topology
with a capacity determined bottleneck
"""
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns

n_iter = 20
bottleneck_bandwidth = []
data = {'00': [], '01': [], '02': [], '03': [], '04': [], '05': []}

bottleneck_link_dest = {'name': 'r3', 'ip': '10.0.3.3'}
server = {'name': 's1', 'ip': '10.0.4.4'}
contesting_client = 'c2'
client = 'c1'

# setup iperf server on bottleneck link destination
os.system(f"docker exec {server['name']} iperf -s &")
# os.system(f"docker exec {bottleneck_link_dest['name']} iperf -s &")

# generate background traffic from c2 to r3 (through r2)
os.system(f"docker exec {client} iperf -t 0 -c {server['ip']} &")
# os.system(f"docker exec {contesting_client} iperf -t 0 -c {bottleneck_link_dest['ip']} &")


for i in range(n_iter):
	result = subprocess.run(['docker', 'exec', client, './pathneck-1.3/pathneck', '-o', server['ip']],
	                        stdout=subprocess.PIPE)
	output = result.stdout.decode('utf-8')
	print(output)
	for line in output.splitlines():
		line = line.split()
		if len(line) == 8:
			if line[5] == '1':
				bottleneck = line[0]
				bottleneck_bw = float(line[6])
				bottleneck_bandwidth.append(float(line[6]))
				data[line[0]].append(bottleneck_bw)

# plot bandwidth test results
total_data = [data[key] for key in data]
sns.stripplot(data=total_data, jitter=True, color='black')
sns.boxplot(total_data)
plt.xlabel('Hop ID')
plt.ylabel('Measured bandwidth ')
plt.title(f'Bandwidth [Mbits/sec] distributions of detected bottlenecks')
plt.savefig('pathneck-boxplot')
plt.show()



