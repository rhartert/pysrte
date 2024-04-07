import random

import srte


def parse(demand_file, network_file) -> srte.Instance:
    inst = srte.Instance()

    with open(network_file) as f:
        lines = f.readlines()
        n_nodes = int(lines[0].strip().split()[1])
        lines = lines[n_nodes + 5 :]
        for line in lines:
            parts = line.strip().split()
            inst.add_edge(
                srte.Edge(
                    src=int(parts[1]),
                    dest=int(parts[2]),
                    weight=1,
                    capacity=int(parts[4]),
                )
            )

    with open(demand_file) as f:
        lines = f.readlines()
        lines = lines[2:]
        for line in lines:
            parts = line.split()
            inst.add_demand(
                srte.Demand(
                    src=int(parts[1]),
                    dest=int(parts[2]),
                    traffic=int(parts[3]),
                )
            )

    return inst


demands_file = "data/synth100.demands"
network_file = "data/synth100.graph"

inst = parse(demands_file, network_file)
cfg = srte.Config(alpha=8.0, beta=4.0, max_nodes=2)
lgs = srte.LgsSolver(inst, cfg)
random.seed(42)

init_util = lgs.max_utilization()
for iter in range(10000):
    if iter <= 1000:
        e = lgs.max_utilized_edge()
    else:
        e = lgs.select_edge(random.random())

    d = lgs.select_demand(e, random.random())
    if not d:
        continue

    move = lgs.search(e, d, lgs.max_utilization())
    if not move:
        continue

    lgs.apply_move(move)

print(f"utilization (before): {init_util}")
print(f"utilization (after):  {lgs.max_utilization()}")
