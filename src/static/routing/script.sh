#!/bin/bash

# Step 1: Read network configuration from a JSON file
config_file="./network-config.json"
nodes=$(cat "$config_file" | jq -c '.nodes')

# Step 2: Create Docker networks for each node
for node in $(echo "$nodes" | jq -c '.[]'); do
    name=$(echo "$node" | jq -r '.name')
    network=$(echo "$node" | jq -r '.network')
    docker network create "$name"_net
done

# Step 3: Start containers and attach them to their networks
for node in $(echo "$nodes" | jq -c '.[]'); do
    name=$(echo "$node" | jq -r '.name')
    image=$(echo "$node" | jq -r '.image')
    network=$(echo "$node" | jq -r '.network')
    docker run -d --name "$name" --network "$name"_net --privileged "$image" tail -f /dev/null
done

# Step 4: Build a graph using the link_name and link_direction
declare -A graph
for node in $(echo "$nodes" | jq -c '.[]'); do
    node_name=$(echo "$node" | jq -r '.name')
    network=$(echo "$node" | jq -r '.network')
    for link in $(echo "$node" | jq -c '.links[]'); do
        link_name=$(echo "$link" | jq -r '.name')
        link_direction=$(echo "$link" | jq -r '.direction')
        if [ "$link_direction" == "out" ]; then
            graph["$node_name-$link_name"]=1
            # docker network connect "$name"_net "$link_name"
            # docker network connect "$link_name"_net "$name" #TODO use subnet 
        else
            graph["$link_name-$node_name"]=1
        fi
    done
done

# Step 5: Determine the path of hops using Dijkstra and add the hops using ip route add
declare -A shortest_paths
for node in $(echo "$nodes" | jq -c '.[]'); do
    node_name=$(echo "$node" | jq -r '.name')
    echo -e "$node_name"
    # echo -e "${graph[*]} \n"
    # echo -e "$(echo "${!graph[@]}")\n\n"
    #python3 dijkstra.py "$node_name" "${graph[*]}" "$(echo "${!graph[@]}")"
    hops=$(python3 dijkstra.py "$node_name" "${graph[*]}" "$(echo "${!graph[@]}")")
    while IFS=',' read -r dest hop; do
        if [[ "$dest" != "" ]]; then
            dest_ip=$(docker exec $dest ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
            next_hop_ip=$(docker exec $hop ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
            docker exec --privileged "$node_name" ip route add "$dest_ip" via "$next_hop_ip" dev eth0
            #TODO create a router connect to connect
            echo "Tuple: $dest_ip $next_hop_ip"
        fi
    done <<< "$hops"
    # shortest_paths["$node_name"]=$hops
    # for hop in $hops; do
    #     ip route add "$hop" via "$(echo "$hops" | grep -B1 "$hop" | head -n1)" dev eth0
    # done
done

# # Print the graph and shortest paths
# echo "Graph:"
# for key in "${!graph[@]}"; do
#     echo "$key: ${graph[$key]}"
# done

# echo "Shortest Paths:"
# for node in $(echo "$nodes" | jq -c '.[]'); do
#     node_name=$(echo "$node" | jq -r '.name')
#     echo "$node_name: ${shortest_paths[$node_name]}"
# done
