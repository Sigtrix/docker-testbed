import docker
import argparse


def disconnect_node(node: str, subnet: str):
	"""
	disconnects node from subnet
	:param node: node to disconnect
	:param subnet: subnet to disconnect from
	:return: None
	"""
	client = docker.from_env()
	container = client.containers.get(node)
	net = client.networks.get(subnet)
	net.disconnect(container.name)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Disconnect node from subnet')
	parser.add_argument('-d', '--disconnect', help='node to disconnect', required=True)
	parser.add_argument('-s', '--subnet', help='subnet to disconnect node from', required=True)

	args = parser.parse_args()

	disconnect_node(args.disconnect, args.subnet)
	print(f"disconnected node {args.disconnect} from subnet {args.subnet}")