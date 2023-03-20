Run command: sudo bash script.sh

To check the IP Addresses of the containers:
docker ps -q | xargs -n 1 docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'