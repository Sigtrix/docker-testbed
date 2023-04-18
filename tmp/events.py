import os
import time
add_link = "python3 setup.py add_link"
remove_link= "python3 setup.py remove_link"

link1 = '(("r1", "10.0.4.2"), ("s1", "10.0.4.4"), (1, 12500, 10))'
link2 = '(("r1", "10.0.2.2"), ("r2", "10.0.2.3"), (1, 12500, 10))'

os.system(f"{add_link} '{link1}'")
time.sleep(5)
os.system(f"{remove_link} '{link2}'")