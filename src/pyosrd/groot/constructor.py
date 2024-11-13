from pyosrd import OSRD
from .groot import Groot
from .build_zones import build_zones, zones_graph
from .get_times import get_times


def from_sim(sim: OSRD) -> Groot:
    g = Groot()
    g.zones, g.stations, g.ends_with_a_signal = build_zones(sim)
    g._zones_graph = zones_graph(g.zones)
    if sim.results:
        g.times, g.min_durations = get_times(sim, g.zones)
    return g
