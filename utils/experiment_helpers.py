"""
Helper functions useful when setting up an experiment
"""
import subprocess


def capture_traffic(node_name, interface, duration, filename):
	"""
	Capture traffic with tcpdump on a node for a given time
	duration and write to file.
	:param node_name: name of node to run tcpdump on
	:param interface: interface to capture traffic on
	:param duration: time to measure traffic in seconds
	:param filename: file to write output to
	:return: None
	"""
	try:
		subprocess.check_call(f"docker exec {node_name} timeout {duration} -i {interface} > {filename} &", shell=True)
	except subprocess.CalledProcessError as e:
		print(f"Command {e.cmd} returned non-zero exit status: {e.returncode}")


def iperf_server(node_name):
	"""
	Starts an iperf server on a node
	:param node_name: name of node to start iperf server on
	:return: None
	"""
	try:
		subprocess.check_call(f'docker exec {node_name} iperf -s &', shell=True)
	except subprocess.CalledProcessError as e:
		print(f"Command {e.cmd} returned non-zero exit status: {e.returncode}")


def iperf_client(node_name, server_ip):
	"""
	Start iperf client on node
	:param node_name: name of client node
	:param server_ip: ip address of server node
	:return: None
	"""
	try:
		subprocess.check_call(f"docker exec {node_name} iperf -t 0 -c {server_ip} &", shell=True)
	except subprocess.CalledProcessError as e:
		print(f"Command {e.cmd} returned non-zero exit status: {e.returncode}")


def pathneck(client_name, server_ip):
	"""
	Run pathneck from client to server
	:param client_name: name of client node
	:param server_ip: ip address of server node
	:return: String containing output of Pathneck
	run with online flag set
	"""
	result = subprocess.run(['docker', 'exec', f'{client_name}', './pathneck-1.3/pathneck', '-o', f'{server_ip}'],
	                        stdout=subprocess.PIPE)
	return result.stdout.decode('utf-8')


def parse_pathneck_result(pathneck_result):
	"""
	Returns detected bottleneck and estimated bandwidth
	:param pathneck_result: result of pathneck run such as output
	of pathneck function
	:return: tuple (bottleneck, bottleneck_bandwidth)
	the detected bottleneck and the estimated bottleneck bandwidth if found,
	else returns None
	"""
	for line in pathneck_result.splitlines():
		line = line.split()
		if len(line) == 8:
			if line[5] == '1':
				bottleneck = line[0]
				bottleneck_bw = float(line[6])
				return bottleneck, bottleneck_bw
	return None, None
