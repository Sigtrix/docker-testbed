"""
Nodes Format:
{node_name: (ip_addr, base_link name), ...}
"""
nodes = {"c1": ("10.0.1.4", "c1-r1"),
         "r1": ("10.0.1.2", "c1-r1"),
         "r2": ("10.0.3.2", "r2-s1"),
         "s1": ("10.0.3.4", "r2-s1")}

"""
Links Format:
[(endpoint_name1, ip1, (endpoint_name2, ip2)), (bandwidth[Mbit/s], burst[kb], latency[ms])), ...]
"""
links = [(("c1", "10.0.1.4"), ("r1", "10.0.1.2"), (1, 2, 10)),
         (("r2", "10.0.3.2"), ("s1", "10.0.3.4"), (1, 2, 10)),
         (("r1", "10.0.2.2"), ("r2", "10.0.2.3"), (1, 2, 10))]