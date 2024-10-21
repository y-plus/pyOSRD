from pyosrd.groot import Groot

def sum_delays_at_end(g: Groot, ref: Groot) -> float:
    return sum(
        g.times[train][g.path(train)[-1]][1]
        - ref.times[train][ref.path(train)[-1]][1]
        for train in ref.times
    )