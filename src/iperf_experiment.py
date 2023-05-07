import os
import time

# Start iperf server in the background
os.system('docker exec r5 iperf -s &')

# Wait for the server to start
time.sleep(1)

# Run iperf client to measure bandwidth
bandwidth_values = []
i = 0
while i < 3:
    result = os.popen('docker exec c2 iperf -t 5 -c 10.0.3.4').read()
    lines = result.splitlines()
    line = lines[6].split()
    bandwidth_values.append(line[6])
    os.system('docker exec c2 pkill iperf')
    time.sleep(3)
    i += 1

# Print the bandwidth values
print('Bandwidth values:', bandwidth_values)

# Stop the iperf server and client
os.system('docker exec c2 pkill iperf')
os.system('docker exec r5 pkill iperf')
