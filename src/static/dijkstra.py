#!/usr/bin/env python3

import sys
from queue import PriorityQueue

# Function to compute the shortest path from a source node to all other nodes in the graph
def dijkstra(graph, start):
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

# Main function to compute the shortest path from a source node to all other nodes in the graph
if __name__ == '__main__':
    start = sys.argv[1]
    weights_str = sys.argv[2]
    connections_str = sys.argv[3]
    weights = weights_str.split()
    connections = connections_str.split()
    # print(start)
    # print(weights)
    # print(connections)
    graph = {}
    for i, node_str in enumerate(connections):
        node = node_str.split('-')
        if node[0] not in graph:
            graph[node[0]] = []
        graph[node[0]].append((node[1], float(weights[i])))
        if node[1] not in graph:
            graph[node[1]] = []
    dist = dijkstra(graph, start)
    # print(dist)
    hops = []
    for node in graph.keys():
        if node == start:
            continue
        prev_node = dist[node][1]
        next_hop = node
        while prev_node != start and dist[prev_node][0]!= float('inf'):
            next_hop = prev_node
            prev_node = dist[prev_node][1]
        if dist[prev_node][0] == float('inf'):
            continue
        hops.append((node,next_hop))
    for tup in hops:
        print(f"{tup[0]},{tup[1]}")
