from pyosrd import OSRD
from .groot import Groot
from .build_zones import build_zones, zones_graph
from .get_times import get_times_and_lengths


def from_sim(sim: OSRD) -> Groot:
    g = Groot()
    g.zones, g.stations = build_zones(sim)
    g._zones_graph = zones_graph(g.zones)
    g.stations = list(sim.station_capacities.keys())
    g.times, g.min_durations, g.lengths = get_times_and_lengths(sim, g.zones)
    return g
