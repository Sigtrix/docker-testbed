#!/bin/bash
python3 setup.py add_link '"r1-s1": ("10.0.4.0/24", (("r1", "10.0.4.2", "eth2"), ("s1", "10.0.4.4", "eth1")), 10)'
sleep 5
python3 setup.py remove_link '"r1-r2": ("10.0.2.0/24", (("r1", "10.0.2.2", "eth1"), ("r2", "10.0.2.3", "eth1")), 10)'