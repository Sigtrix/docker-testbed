import os
from config import nodes, links


def build_image(img_name, img_path):
	"""
	Build docker image
	:param img_name: name of image
	:param img_path: path of Dockerfile
	:return: None
	"""
	cmd = f"docker build -t {img_name} {img_path}"
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
	os.system(cmd)


def create_subnet(ip_range, subnet_name):
	"""
	Create subnet
	:param ip_range: range of ips on subnet
	:param subnet_name: name of subnet
	:return: None
	"""
	cmd = f"docker network create --subnet={ip_range} {subnet_name}"
	os.system(cmd)


def attach(ip, subnet_name, container_name):
	"""
	Attach container to subnet
	:param ip: ip of container on subnet
	:param subnet_name: name of subnet
	:param container_name: name of container
	:return: None
	"""
	cmd = f"docker network connect --ip {ip} {subnet_name} {container_name}"
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
	os.system(cmd)


# build router, client and server images
for _, node_param in nodes.items():
	image = node_param[1]
	build_image(image[0], image[1])


# create subnets
for link_name, link_param in links.items():
	create_subnet(link_param[0], link_name)

# create containers
for node_name, node_param in nodes.items():
	create_container(node_name, node_param[1][0], node_param[2], node_param[0])

# attach containers to networks
for link_name, link_param in links.items():
	endpoints = link_param[1]
	attach(endpoints[0][1], link_name, endpoints[0][0])
	attach(endpoints[1][1], link_name, endpoints[1][0])

# TODO: configure bandwidth of links

# TODO: Use Dijkstra to configure routing tables with add route function above
