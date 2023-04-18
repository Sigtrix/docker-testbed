all: clean setup run test

clean:
	for node in $$(jq -r '.nodes | keys[]' state.json); do \
        docker rm -f $${node} ; \
    done
	docker network prune -f
	echo '{}' > state.json

setup:
	python3 setup.py

run:
	python3 events.py

test:
	docker exec -it c1 traceroute 10.0.4.4