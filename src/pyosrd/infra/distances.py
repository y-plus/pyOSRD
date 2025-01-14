import networkx as nx

def distance_between_points(
    self,
    point1_id: str,
    point2_id: str,
    track_section_lengths: dict[str, float],
    track_section_network: nx.DiGraph,
) -> float:

    p1 = self.get_point(point1_id)
    p2 = self.get_point(point2_id)

    if p1.track_section == p2.track_section:
        return abs(p2.position - p1.position)

    path = nx.shortest_path(
        track_section_network, p1.track_section, p2.track_section
    )

    in_by = nx.get_edge_attributes(track_section_network, 'in_by')
    out_by = nx.get_edge_attributes(track_section_network, 'out_by')

    distance = (
        track_section_lengths[path[0]] - p1.position
        if out_by[(path[0], path[1])] == 'END'
        else p1.position
    )

    for t in path[1:-1]:
        distance += track_section_lengths[t]

    distance += (
        p2.position
        if in_by[(path[-2], path[-1])] == 'BEGIN'
        else track_section_lengths[path[-1]] - p2.position
    )

    return distance