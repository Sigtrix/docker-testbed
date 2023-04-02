docker exec {server['name']} iperf -s &

bandwidth, burst, latency = tc_params
#Default value 2 for each of them.

docker exec {node} tc qdisc add dev {interface} \
root handle 1: tbf rate {bandwidth}mbit burst {burst}kb latency {latency}ms

docker exec {node} tc qdisc add dev {interface} \
parent 1:1 handle 10: netem delay {latency}ms

docker exec client iperf -c server['ip']

docker exec client ping -c 10 server['ip']