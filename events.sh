python3 setup.py add_link '(("r1", "10.0.4.2"), ("s1", "10.0.4.4"), 10)'
sleep 5
python3 setup.py remove_link '(("r1", "10.0.2.2"), ("r2", "10.0.2.3"), 10)'