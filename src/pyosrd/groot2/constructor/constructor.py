# from pyosrd import OSRD
from ..groot import Groot
from .build_zones import build_zones, zones_graph, tvds_graph
from .get_times import get_times


def from_sim(sim) -> Groot:
    g = Groot()
    g.zones, g.stations, g.ends_with_a_signal = build_zones(sim)
    g._zones_graph = zones_graph(g.zones)
    g._tvds_graph = tvds_graph(g.zones, g.ends_with_a_signal)
    g._sim = sim
    g._track_section_network = sim._track_section_network
    g._track_section_lengths = sim.track_section_lengths
    if sim.results:
        g.times, g.min_durations = get_times(sim, g.zones)
    return g
