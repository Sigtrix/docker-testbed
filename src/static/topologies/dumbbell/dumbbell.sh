#!/usr/bin/env bash

set -eux

# stop and remove containers only if exist
nodelist=(c1 c2 s1 s2 r1 r2)
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
networklist=(c1-r1 c2-r1 r1-r2 r2-s1 r2-s2)
for i in "${networklist[@]}"
do
	if [ "$(docker network ls | grep $i)" ];then
        	docker network rm $i
	fi
done

# build router, client and server images
docker build -t dumbbell-image .

# create subnets
docker network create --subnet=20.0.1.0/24 c1-r1
docker network create --subnet=20.0.2.0/24 c2-r1
docker network create --subnet=20.0.3.0/24 r1-r2
docker network create --subnet=20.0.4.0/24 r2-s1
docker network create --subnet=20.0.5.0/24 r2-s2

# attach containers to networks
docker run -d --name r1 --network c1-r1 --ip 20.0.1.2 --privileged dumbbell-image
docker network connect --ip 20.0.2.2 c2-r1 r1
docker network connect --ip 20.0.3.2 r1-r2 r1

docker run -d --name r2 --network r2-s1 --ip 20.0.4.2 --privileged dumbbell-image
docker network connect --ip 20.0.5.2 r2-s2 r2
docker network connect --ip 20.0.3.3 r1-r2 r2

docker run -d --name c1 --network c1-r1 --ip 20.0.1.4 --privileged dumbbell-image
docker run -d --name c2 --network c2-r1 --ip 20.0.2.4 --privileged dumbbell-image
docker run -d --name s1 --network r2-s1 --ip 20.0.4.4 --privileged dumbbell-image
docker run -d --name s2 --network r2-s2 --ip 20.0.5.4 --privileged dumbbell-image

# configure routing tables
docker exec c1 ip route add 20.0.4.0/24 via 20.0.1.2 dev eth0
docker exec c1 ip route add 20.0.5.0/24 via 20.0.1.2 dev eth0

docker exec c2 ip route add 20.0.4.0/24 via 20.0.2.2 dev eth0
docker exec c2 ip route add 20.0.5.0/24 via 20.0.2.2 dev eth0

docker exec r1 ip route add 20.0.4.0/24 via 20.0.3.3 dev eth2
docker exec r1 ip route add 20.0.5.0/24 via 20.0.3.3 dev eth2

docker exec r2 ip route add 20.0.1.0/24 via 20.0.3.2 dev eth2
docker exec r2 ip route add 20.0.2.0/24 via 20.0.3.2 dev eth2
docker exec r2 ip route change 20.0.4.0/24 via 20.0.4.4 dev eth0
docker exec r2 ip route change 20.0.5.0/24 via 20.0.5.4 dev eth1

docker exec s1 ip route add 20.0.1.0/24 via 20.0.4.2 dev eth0
docker exec s1 ip route add 20.0.2.0/24 via 20.0.4.2 dev eth0
docker exec s2 ip route add 20.0.1.0/24 via 20.0.5.2 dev eth0
docker exec s2 ip route add 20.0.2.0/24 via 20.0.5.2 dev eth0

docker ps
