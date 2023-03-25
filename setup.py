import os
import sys
import ast
from config import nodes, links
from queue import PriorityQueue

def dijkstra(graph, start):
    """Function to compute the shortest path from a source node to all other nodes in the graph"""
    # Initialize the distance dictionary and set the distance of the start node to 0
    dist = {}
    for node in graph:
        dist[node] = [float('inf'),node]
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
            distance = current_dist + weight
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


def create_container(container_name, img_name):
    """
    Create and start container
    :param container_name: name of container
    :param ip: container ip address
    :param img_name: name of image
    :return: None
    """
    cmd = f"docker run -d --name {container_name}" \
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


def attach(ip, subnet_name, container_name):
    """
    Attach container to subnet
    :param subnet_name: name of subnet
    :param container_name: name of container
    :return: None
    """
    cmd = f"docker network connect --ip {ip} {subnet_name} {container_name}"
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
    print(cmd)
    os.system(cmd)


if __name__ == "__main__":
    node_vs_ip = {}
    for node_name, node_param in nodes.items():
        node_vs_ip[node_name] = node_param[0]
    # python3 setup.py add_link '"r2-s1": ("10.0.3.0/24", (("r2", "10.0.3.2", "eth2"), ("s1", "10.0.3.4", "eth1")), 10)'
    if len(sys.argv) == 3:
        print(sys.argv[1])
        print(sys.argv[2])
        if(str(sys.argv[1])=="add_link"):
            link = sys.argv[2].split(":")
            link_name = ast.literal_eval(link[0])
            link_param_str = link[1]
            link_param = ast.literal_eval(link_param_str)
            links[link_name] = link_param
            create_subnet(link_param[0], link_name)
            # for node_name, node_param in nodes.items():
            #     create_container(node_name, node_param[1][0])
            endpoints = link_param[1]
            attach(endpoints[0][1], link_name, endpoints[0][0])
            attach(endpoints[1][1], link_name, endpoints[1][0])
        else:
            print("Invalid Argument")
    else:
        # build router, client and server images
        for node_name, node_param in nodes.items():
            image = node_param[1]
            build_image(image[0], image[1])

        # create subnets
        for link_name, link_param in links.items():
            create_subnet(link_param[0], link_name)

        # create containers
        for node_name, node_param in nodes.items():
            create_container(node_name, node_param[1][0])

        # attach containers to networks
        for link_name, link_param in links.items():
            endpoints = link_param[1]
            try:
                attach(endpoints[0][1], link_name, endpoints[0][0])
                attach(endpoints[1][1], link_name, endpoints[1][0])
            except Exception as e:
                print(e)

    # TODO: configure bandwidth of links

    # TODO: Use Dijkstra to configure routing tables with add route function above
    graph = {}
    connections = {}
    # Create Graph
    for link_name, link_param in links.items():
        endpoints = link_param[1]
        band_width = link_param[2]
        if endpoints[0][0] not in graph:
            graph[endpoints[0][0]] = []
            connections[endpoints[0][0]] = {}
        graph[endpoints[0][0]].append((endpoints[1][0], float(band_width)))
        connections[endpoints[0][0]][endpoints[1][0]] = (endpoints[1][1], endpoints[0][2]) #ip of other node,eth of itself
        if endpoints[1][0] not in graph:
            graph[endpoints[1][0]] = []
            connections[endpoints[1][0]] = {}
        graph[endpoints[1][0]].append((endpoints[0][0], float(band_width)))
        connections[endpoints[1][0]][endpoints[0][0]] = (endpoints[0][1], endpoints[1][2])

    for start_node in graph:
        dist = dijkstra(graph, start_node)
        hops = []
        for node in graph:
            if node == start_node:
                continue
            prev_node = dist[node][1]
            next_hop = node
            while prev_node != start_node and dist[prev_node][0]!= float('inf'):
                next_hop = prev_node
                prev_node = dist[prev_node][1]
            if dist[prev_node][0] == float('inf'):
                continue
            hops.append((node,next_hop))
        print(f"\nStart Node = {start_node}")
        for dest_node, next_hop_node in hops:
            dest_node_ip = node_vs_ip[dest_node]
            next_hop_node_ip = connections[start_node][next_hop_node][0]
            interface = connections[start_node][next_hop_node][1]
            add_route(start_node, dest_node_ip, next_hop_node_ip, interface)
            print(f"Destination Node = {dest_node}, Next hop = {next_hop_node}")

