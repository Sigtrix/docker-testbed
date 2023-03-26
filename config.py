import os
linear_dir = os.path.join("src", "topologies", "linear")
#TODO: Remove "c1-r1" parameter
#TODO: Remove linear_dir and image name
nodes = {"c1": ("10.0.1.4", ("client-image", os.path.join(linear_dir, "c1")), "c1-r1"),
         "r1": ("10.0.1.2", ("router-image", os.path.join(linear_dir, "r")), "c1-r1"),
         "r2": ("10.0.3.2", ("router-image", os.path.join(linear_dir, "r")), "r2-s1"),
         "s1": ("10.0.3.4", ("server-image", os.path.join(linear_dir, "s1")), "r2-s1")}
"""
{node_name: (ip_addr, (image_name, image_path), eth0_network), ...}
"""
links = [(("c1", "10.0.1.4"), ("r1", "10.0.1.2"), 10),
         (("r2", "10.0.3.2"), ("s1", "10.0.3.4"), 10),
         (("r1", "10.0.2.2"), ("r2", "10.0.2.3"), 10)]
"""
{subnet_name: (ip_range, ((endpoint_name1, ip1, interface), (endpoint_name2, ip2, interface)), bandwidth), ...}
"""

#Removed link name "c1-r1"
#Removed interface "eth0"
#Made IP allocation automated
#Removed subnet "10.0.1.0/24"
# links = {"c1-r1": ("10.0.1.0/24", (("c1", "10.0.1.4", "eth0"), ("r1", "10.0.1.2", "eth0")), 10),
#          "r1-r2": ("10.0.2.0/24", (("r1", "10.0.2.2", "eth1"), ("r2", "10.0.2.3", "eth1")), 10),
#          "r2-s1": ("10.0.3.0/24", (("r2", "10.0.3.2", "eth0"), ("s1", "10.0.3.4", "eth0")), 10)} Wrong
# links = {"c1-r1": ("10.0.1.0/24", (("c1", "10.0.1.4", "eth0"), ("r1", "10.0.1.2", "eth0")), 10),
#          "r2-s1": ("10.0.3.0/24", (("r2", "10.0.3.2", "eth0"), ("s1", "10.0.3.4", "eth0")), 10),
#          "r1-r2": ("10.0.2.0/24", (("r1", "10.0.2.2", "eth1"), ("r2", "10.0.2.3", "eth1")), 10)} Right