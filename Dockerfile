FROM ubuntu:latest

# Update the package list and install the necessary packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    iproute2 \
    iputils-ping \
    traceroute \
    iperf \
    vim \
    wget \
    make \
    gcc \
    build-essential \
    tcpdump \
    python3

# Install Pathneck
RUN wget http://www.cs.cmu.edu/~hnn/pathneck/pathneck-1.3.tgz && \
    tar -xf pathneck-1.3.tgz && \
    cd pathneck-1.3 && \
    make

# Start a shell and keep the container running
CMD ["tail", "-f", "/dev/null"]
