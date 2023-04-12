"""
Nodes Format:
{node_name: (ip_addr, base_link name), ...}
"""
nodes = {"c1": ("10.0.1.2", "c1-r1"),
        "c2": ("10.0.2.2", "c2-r1"),
        "r1": ("10.0.1.4", "c1-r1"),
        "r2": ("10.0.3.2", "r2-s1"),
        "s1": ("10.0.3.4", "r2-s1"),
        "s2": ("10.0.4.4", "r2-s2") }

"""
Links Format:
[(endpoint_name1, ip1, (endpoint_name2, ip2)), (bandwidth[Mbit/s], burst[kb], latency[ms])), ...]
"""
links = [(("c1", "10.0.1.2"), ("r1", "10.0.1.4"), (1, 12500, 10)),
        (("c2", "10.0.2.2"), ("r1", "10.0.2.4"), (1, 12500, 10)),
        (("r2", "10.0.3.2"), ("s1", "10.0.3.4"), (1, 12500, 10)),
        (("r2", "10.0.4.2"), ("s2", "10.0.4.4"), (1, 12500, 10)),
        (("r1", "10.0.5.2"), ("r2", "10.0.5.4"), (1, 12500, 10))]