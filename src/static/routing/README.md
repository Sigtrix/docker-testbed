Run command: sudo bash script.sh

To check the IP Addresses of the containers:
docker ps -q | xargs -n 1 docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
docker exec -it c1 traceroute 10.0.3.4
docker exec -it c1 ip route
docker exec -it c1 /bin/bash
