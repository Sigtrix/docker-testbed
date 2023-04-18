all: clean setup run

clean:
	for node in $$(jq -r '.nodes | keys[]' ./tmp/state.json); do \
        docker rm -f $${node} ; \
    done
	docker network prune -f
	echo '{}' > ./tmp/state.json

setup:
	python3 ./src/setup.py --config $(CONFIG)

run:
	python3 ./tmp/events.py