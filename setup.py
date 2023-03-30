import os
import sys
import ast
import config
from queue import PriorityQueue
import json


def dijkstra(graph, start):
	"""
	Function to compute the shortest path from a source node to all other nodes in the graph
	param: graph: the graph of the network
	param: start: the source/start node from where minimum distance to other nodes is calculated.
	return: Distance dictionary, where each element is a tuple of distance from source node and 
	the previous node in the shortest path from the source.
	"""
	# Initialize the distance dictionary and set the distance of the start node to 0
	dist = {}
	for node in graph:
		dist[node] = [float('inf'), node]
	dist[start][0] = 0

	# Initialize the priority queue and add the start node with distance 0
	pq = PriorityQueue()
	pq.put((0, start))

	# Traverse the graph using BFS and update the distance for each neighbor node
	while not pq.empty():
		current_dist, current_node = pq.get()
		if current_dist > dist[current_node][0]:
			continue
		for neighbor, weight in graph[current_node]:
			# weights are bandwidth values
			distance = current_dist + weight[0]
			if distance < dist[neighbor][0]:
				dist[neighbor] = [distance, current_node]
				pq.put([distance, neighbor])

	# Return the distance dictionary
	return dist


def build_image(img_name, img_path):
	"""
	Build docker image
	:param img_name: name of image
	:param img_path: path of Dockerfile
	:return: None
	"""
	cmd = f"docker build -t {img_name} {img_path}"
	print(cmd)
	os.system(cmd)


def create_container(container_name, img_name, network, ip):
	"""
	Create and start container
	:param container_name: name of container
	:param ip: container ip address
	:param img_name: name of image
	:param network: network name on eth0 interface
	:param ip: ip address of node on <network>
	:return: None
	"""
	cmd = f"docker run -d --name {container_name}" \
	      f" --network {network}" \
	      f" --ip {ip}" \
	      f" --privileged {img_name}"
	print(cmd)
	os.system(cmd)


def create_subnet(ip_range, subnet_name):
	"""
	Create subnet
	:param ip_range: range of ips on subnet
	:param subnet_name: name of subnet
	:return: None
	"""
	cmd = f"docker network create --subnet={ip_range} {subnet_name}"
	print(cmd)
	os.system(cmd)


def remove_subnet(subnet_name):
	"""
	Remove subnet
	:param subnet_name: name of subnet
	:return: None
	"""
	cmd = f"docker network rm {subnet_name}"
	print(cmd)
	os.system(cmd)


def attach(ip, subnet_name, container_name, interface, tc_params):
	"""
	Attach container to subnet
	:param subnet_name: name of subnet
	:param container_name: name of container
	:param tc_params: tuple (bandwidth, burst, latency)
	:return: None
	"""
	if interface == "eth0":
		configure_link(container_name, interface, tc_params)
	else:
		cmd = f"docker network connect --ip {ip} {subnet_name} {container_name}"
		print(cmd)
		os.system(cmd)
		configure_link(container_name, interface, tc_params)


def detach(subnet_name, container_name):
	"""
	Detach container from a subnet
	:param subnet_name: name of subnet
	:param container_name: name of container
	:return: None
	"""
	cmd = f"docker network disconnect {subnet_name} {container_name}"
	print(cmd)
	os.system(cmd)


def add_route(container_name, ip_range, gateway_ip, interface):
	"""
	Add routing rule for packets from a container to a subnet
	:param container_name: name of src container
	:param ip_range: destination subnet
	:param gateway_ip: ip of next hop gateway
	:param interface: interface through which packets will be sent
	:return: None
	"""
	cmd = f"docker exec {container_name} ip route add {ip_range}" \
	      f" via {gateway_ip} dev {interface}"
	cmdValue = os.system(cmd)
	if cmdValue != 0:
		cmd = f"docker exec {container_name} ip route change {ip_range}" \
		      f" via {gateway_ip} dev {interface}"
		os.system(cmd)


def del_route(container_name, ip_range):
	"""
	Deleting routing rule corresponding to a link
	:param container_name: name of src container
	:param ip_range: destination node ip address
	:return: None
	"""
	cmd = f"docker exec {container_name} ip route delete {ip_range}"
	os.system(cmd)


def write_state_json(nodes, links, node_vs_ip, node_vs_eth):
	"""
	Reads from the current state (consisting of all the input parameters of this function)
	and stores it in the state.json file
	:param nodes: node information in the format as defined in json file.
	:param links: link information in the format as defined in json file.
	:param node_vs_ip: list of ips associated with the nodes
	:param: node_vs_eth: the highest ethernet interface number used.
	:return: the current state of the graph in dictionary format
	"""
	with open("state.json", "w") as f:
		json.dump({"nodes": nodes, "links": links, "node_vs_ip": node_vs_ip, "node_vs_eth": node_vs_eth}, f, indent=4)


def read_state_json():
	"""
	Read the state json file which stores the current state.
	:param: None
	:return: the current state of the graph in dictionary format
	"""
	with open("state.json", "r") as f:
		current_state = json.load(f)
	return current_state


def generate_link_param(node_vs_eth, link_info):
	"""
	Generates more parameters from the limited set of info taken form config file.
	:param node_vs_eth: contains the node vs ethernet number mapping to decide the next
	ethernet available to use for the link.
	:param link_info: contains the info provided for the link in the config file or add
	and delete link commands.
	:return: link_name, node_vs_eth, link_param
	"""
	node0 = link_info[0]
	node1 = link_info[1]
	link_name = node0[0] + "-" + node1[0]
	subnet_ip = ".".join(node0[1].split(".")[:3]) + ".0/24"
	if node0[0] not in node_vs_eth:
		node_vs_eth[node0[0]] = 0
	else:
		node_vs_eth[node0[0]] += 1
	if node1[0] not in node_vs_eth:
		node_vs_eth[node1[0]] = 0
	else:
		node_vs_eth[node1[0]] += 1
	link_param = (subnet_ip, ((node0[0], node0[1], "eth" + str(node_vs_eth[node0[0]])),
	                          (node1[0], node1[1], "eth" + str(node_vs_eth[node1[0]]))), link_info[2])
	return link_name, node_vs_eth, link_param


def configure_link(node, interface, tc_params):
	"""
	Configure interface on node
	:param node: node to configure
	:param interface: interface to configure
	:param tc_params: tuple (bandwidth, burst, latency)
	:return: None
	"""
	bandwidth, burst, latency = tc_params
	cmd_bandwidth = f"docker exec {node} tc qdisc add dev {interface} " \
	      f"root handle 1: tbf rate {bandwidth}mbit burst {burst}kb latency {latency}ms"
	cmd_latency = f"docker exec {node} tc qdisc add dev {interface} " \
	              f"parent 1:1 handle 10: netem delay {latency}ms"
	cmd_value_bandwidth = os.system(cmd_bandwidth)
	cmd_value_latency = os.system(cmd_latency)
	# Error handling for cmd_bandwidth and cmd_latency
	if cmd_value_bandwidth != 0 or cmd_value_latency != 0:
		clear_child = f"docker exec {node} tc qdisc del dev {interface} parent 1:1 handle 10"
		clear_cmd = f"docker exec {node} tc qdisc del dev {interface} root"
		os.system(clear_child)
		os.system(clear_cmd)
		os.system(cmd_bandwidth)
		os.system(cmd_latency)


if __name__ == "__main__":
	node_vs_ip = {}
	node_vs_eth = {}
	for node_name, node_param in config.nodes.items():
		if node_name not in node_vs_ip:
			node_vs_ip[node_name] = []
		node_vs_ip[node_name].append(node_param[0])
	if len(sys.argv) == 3:
		print(sys.argv[1])
		print(sys.argv[2])
		# Handling add_link functionality
		if (str(sys.argv[1]) == "add_link"):
			current_state = read_state_json()
			node_vs_eth = current_state["node_vs_eth"]
			link_info = ast.literal_eval(sys.argv[2])
			link_name, node_vs_eth, link_param = generate_link_param(node_vs_eth, link_info)
			current_state["links"][link_name] = link_param
			links = current_state["links"]
			nodes = current_state["nodes"]
			create_subnet(link_param[0], link_name)
			endpoints = link_param[1]
			tc_params = link_param[2]
			attach(endpoints[0][1], link_name, endpoints[0][0], endpoints[0][2], tc_params)
			attach(endpoints[1][1], link_name, endpoints[1][0], endpoints[1][2], tc_params)
		# Handling remove_link functionality
		elif (str(sys.argv[1]) == "remove_link"):
			current_state = read_state_json()
			node_vs_eth_not_used = {}
			link_info = ast.literal_eval(sys.argv[2])
			link_name, node_vs_eth_not_used, link_param = generate_link_param(node_vs_eth_not_used, link_info)
			node_vs_eth = current_state["node_vs_eth"]
			endpoints = link_param[1]
			if link_name in current_state["links"]:
				start_node = endpoints[0][0]
				dest_node = endpoints[1][0]
				# deleting direct connections due to this link in routing tables
				for dest_node_ip in current_state["node_vs_ip"][dest_node]:
					del_route(start_node, dest_node_ip)
				# because bidirectional
				for start_node_ip in current_state["node_vs_ip"][start_node]:
					del_route(dest_node, start_node_ip)
				# deleting from links data structure
				del current_state["links"][link_name]
			else:
				print("Link being deleted not present.")
				exit()
			links = current_state["links"]
			nodes = current_state["nodes"]
			detach(link_name, endpoints[0][0])
			detach(link_name, endpoints[1][0])
			remove_subnet(link_name)  # remove subnet after detaching containers or containers will get killed.
		else:
			print("Invalid Argument")
	# Reading and storing information from the config.py file
	else:
		# update links to include interface and link_name
		links = {}
		for link_info in config.links:
			link_name, node_vs_eth, link_param = generate_link_param(node_vs_eth, link_info)
			links[link_name] = link_param
		nodes = config.nodes
		# build image for node
		build_image("node-image", ".")

		# create subnets
		for link_name, link_param in links.items():
			create_subnet(link_param[0], link_name)

		# create containers
		for node_name, node_param in nodes.items():
			create_container(node_name, "node-image", node_param[1], node_param[0])

		# attach containers to networks
		for link_name, link_param in links.items():
			endpoints = link_param[1]
			tc_params = link_param[2]
			try:
				attach(endpoints[0][1], link_name, endpoints[0][0], endpoints[0][2], tc_params)
				attach(endpoints[1][1], link_name, endpoints[1][0], endpoints[1][2], tc_params)
			except Exception as e:
				print(e)

	# TODO: configure bandwidth of links

	# Using Dijkstra to configure routing tables with add route function above
	graph = {}
	connections = {}
	# Create Graph
	for link_name, link_param in links.items():
		endpoints = link_param[1]
		tc_params = link_param[2]

		if endpoints[0][0] not in node_vs_ip:
			node_vs_ip[endpoints[0][0]] = []
		node_vs_ip[endpoints[0][0]].append(endpoints[0][1])
		if endpoints[1][0] not in node_vs_ip:
			node_vs_ip[endpoints[1][0]] = []
		node_vs_ip[endpoints[1][0]].append(endpoints[1][1])

		if endpoints[0][0] not in graph:
			graph[endpoints[0][0]] = []
			connections[endpoints[0][0]] = {}
		graph[endpoints[0][0]].append((endpoints[1][0], tc_params))
		connections[endpoints[0][0]][endpoints[1][0]] = (
		endpoints[1][1], endpoints[0][2])  # ip of other node,eth of itself
		if endpoints[1][0] not in graph:
			graph[endpoints[1][0]] = []
			connections[endpoints[1][0]] = {}
		graph[endpoints[1][0]].append((endpoints[0][0], tc_params))
		connections[endpoints[1][0]][endpoints[0][0]] = (endpoints[0][1], endpoints[1][2])

	for start_node in graph:
		dist = dijkstra(graph, start_node)
		hops = []
		for node in graph:
			if node == start_node:
				continue
			prev_node = dist[node][1]
			next_hop = node
			while prev_node != start_node and dist[prev_node][0] != float('inf'):
				next_hop = prev_node
				prev_node = dist[prev_node][1]
			if dist[prev_node][0] == float('inf'):
				continue
			hops.append((node, next_hop))
		print(f"\nStart Node = {start_node}")
		for dest_node, next_hop_node in hops:
			next_hop_node_ip = connections[start_node][next_hop_node][0]
			interface = connections[start_node][next_hop_node][1]
			for dest_node_ip in node_vs_ip[dest_node]:
				add_route(start_node, dest_node_ip, next_hop_node_ip, interface)
			print(f"Destination Node = {dest_node}, Next hop = {next_hop_node}")

	# Store the current state to state.json file
	write_state_json(nodes, links, node_vs_ip, node_vs_eth)
