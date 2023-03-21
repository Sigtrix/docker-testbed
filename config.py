import os

linear_dir = os.path.join("src", "topologies", "linear")


nodes = {"c1": ("10.0.1.4", ("client-image", os.path.join(linear_dir, "c1")), "c1-r1"),
         "r1": ("10.0.1.2", ("router-image", os.path.join(linear_dir, "r")), "c1-r1"),
         "r2": ("10.0.3.2", ("router-image", os.path.join(linear_dir, "r")), "r2-s1"),
         "s1": ("10.0.3.4", ("server-image", os.path.join(linear_dir, "s1")), "r2-s1")}
"""
{node_name: (ip_addr, (image_name, image_path)), ...}
"""

links = {"c1-r1": ("10.0.1.0/24", (("c1", "10.0.1.4", "eth0"), ("r1", "10.0.1.2", "eth0")), 10),
         "r1-r2": ("10.0.2.0/24", (("r1", "10.0.2.2", "eth1"), ("r2", "10.0.2.3", "eth0")), 10),
         "r2-s1": ("10.0.3.0/24", (("r2", "10.0.3.2", "eth1"), ("s1", "10.0.3.4", "eth0")), 10)}
"""
{subnet_name: (ip_range, ((endpoint_name1, ip1), (endpoint_name2, ip2)), bandwidth), ...}
"""

"""
attach containers in the order of the links
"""

