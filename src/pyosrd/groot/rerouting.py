import networkx as nx
from pyosrd.groot import Groot

# def reroute_train_to_avoid_zone(self: Groot, train: str, zone: str) -> Groot:

#     next_station = self.next_station(train, zone)
#     next_next_station = self.next_station(train, next_station) if next_station else None
#     prev_station = self.previous_station(train, zone)
#     prev_prev_station = self.previous_station(train, prev_station) if prev_station else None

#     if prev_station is None and zone != self.train_zones(train)[0]:
#         prev_station = self.train_zones(train)[0]
#     if next_station is None and zone != self.train_zones(train)[-1]:
#         next_station = self.train_zones(train)[-1]

#     graph = self.zones_graph
#     subg = nx.subgraph(graph, [n for n in graph if n!=zone])
#     found = False
#     for n1, n2 in [(prev_station, next_station), (prev_prev_station, next_station), (prev_station, next_next_station)]:
#         if n1 and n2:
#             if found:= nx.has_path(subg, source=n1, target=n2):
#                 source, target = n1, n2
#                 break
#     if not found:
#         return []

#     while nx.has_path(subg, source=source, target=target):
#         zones = nx.shortest_path(subg, source, target)
#         new_zones = [zone for zone in zones if zone not in self.train_zones(train)]
#         alt_zones = zones[zones.index(new_zones[0])-1:zones.index(new_zones[-1])+2]
#         rerouted = self.reroute(train, alt_zones)
#         _, _, conflict, _ = rerouted.earliest_conflict()
#         if conflict in alt_zones:
#             subg = nx.subgraph(subg, [n for n in subg if n!=conflict])
#         else:
#             return rerouted
#     return None

def reroute_train_to_avoid_zone(self: Groot, train: str, zone: str) -> Groot:

    tvd = self.get_tvd(train, zone)
    next_station = self.next_station(train, zone)
    next_next_station = self.next_station(train, next_station) if next_station else None
    prev_station = self.previous_station(train, zone)
    prev_prev_station = self.previous_station(train, prev_station) if prev_station else None

    if prev_station is None and zone != self.train_zones(train)[0]:
        prev_station = self.train_zones(train)[0]
    if next_station is None and zone != self.train_zones(train)[-1]:
        next_station = self.train_zones(train)[-1]

    tvd_prev_station = self.get_tvd(train, prev_station)
    tvd_next_station = self.get_tvd(train, next_station)
    
    tvd_prev_prev_station = (
        self.get_tvd(train, prev_prev_station)
        if prev_prev_station
        else None
    )
    tvd_next_next_station = (
        self.get_tvd(train, next_next_station)
        if next_next_station
        else None
    )

    graph = self.tvds_graph
    subg = nx.subgraph(graph, [n for n in graph if n!=tvd])
    found = False
    for n1, n2 in [
        (tvd_prev_station, tvd_next_station),
        (tvd_prev_prev_station, tvd_next_station),
        (tvd_prev_station, tvd_next_next_station)
    ]:
        if n1 and n2:
            if found:= nx.has_path(subg, source=n1, target=n2):
                source, target = n1, n2
                break
    if not found:
        return []
    
    # while nx.has_path(subg, source=source, target=target):
    if nx.has_path(subg, source=source, target=target):

        tvds = nx.shortest_path(subg, source, target)
        # print(tvds)
        train_path = self.path(train)
        new_tvds = [tvd for tvd in tvds if tvd not in train_path]
        rerouted_path = tvds[tvds.index(new_tvds[0])-1:tvds.index(new_tvds[-1])+2]
        original_path = train_path[
            train_path.index(rerouted_path[0])
            :
            train_path.index(rerouted_path[-1])+1
        ]
        for tvd in rerouted_path:
            print(tvd)
        print()
        for tvd in original_path:
            print(tvd)
    #     rerouted = self.reroute(train, alt_zones)
    #     _, _, conflict, _ = rerouted.earliest_conflict()
    #     if conflict in alt_zones:
    #         subg = nx.subgraph(subg, [n for n in subg if n!=conflict])
    #     else:
    #         return rerouted
    # return None
