FROM ubuntu:latest

# Update the package list and install the necessary packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    iproute2 \
    iputils-ping \
    traceroute \
    iperf

# Start a shell to keep the container running
CMD ["tail", "-f", "/dev/null"]
