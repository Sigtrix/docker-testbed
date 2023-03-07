#!/usr/bin/env bash

set -eux

# stop and remove containers only if exist
nodelist=(c1 r1 r2 s1)
for i in "${nodelist[@]}"
do
	if [ ! "$(docker ps | grep $i)" ]; then
    		if [ "$(docker ps -aq -f name=$i)" ]; then
        		docker rm $i
    		fi
	else
  		docker rm --force $i
	fi
done

# remove networks only if exist
networklist=(c1-r1 r1-r2 r2-s1)
for i in "${networklist[@]}"
do
	if [ "$(docker network ls | grep $i)" ];then
        	docker network rm $i
	fi
done

# build router, client and server images
docker build -t router-image ./r
docker build -t client-image ./c1
docker build -t server-image ./s1

# create subnets
docker network create --subnet=10.0.1.0/24 c1-r1
docker network create --subnet=10.0.2.0/24 r1-r2
docker network create --subnet=10.0.3.0/24 r2-s1

# attach containers to networks
docker run -d --name r1 --network c1-r1 --ip 10.0.1.2 --privileged router-image
docker network connect --ip 10.0.2.2 r1-r2 r1
docker run -d --name r2 --network r2-s1 --ip 10.0.3.2 --privileged router-image
docker network connect --ip 10.0.2.3 r1-r2 r2
docker run -d --name c1 --network c1-r1 --ip 10.0.1.4 --privileged client-image
docker run -d --name s1 --network r2-s1 --ip 10.0.3.4 --privileged server-image

# configure routing tables
docker exec c1 ip route add 10.0.3.0/24 via 10.0.1.2 dev eth0
docker exec r1 ip route add 10.0.3.0/24 via 10.0.2.3 dev eth1
docker exec r2 ip route add 10.0.1.0/24 via 10.0.2.2 dev eth1
docker exec r2 ip route change 10.0.3.0/24 via 10.0.3.4 dev eth0
docker exec s1 ip route add 10.0.1.0/24 via 10.0.3.2 dev eth0

docker ps
