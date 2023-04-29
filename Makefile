all: clean setup run

clean:
	for node in $$(jq -r '.nodes | keys[]' ./tmp/state.json); do \
        docker rm -f $${node} ; \
    done
	docker network prune -f
	echo '{}' > ./tmp/state.json

setup:
	cd src && python3 setup.py

run:
	cd src && python3 experiment.py

test:
	python3 $(TESTSCRIPT)