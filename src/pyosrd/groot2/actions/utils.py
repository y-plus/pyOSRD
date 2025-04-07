 
from ..groot import Groot


def head_to_head(
    groot: Groot,
    train1: str,
    train2: str,
    zone: str
) -> bool:
    tvd1 = groot.get_tvd(train1, zone)
    tvd2 = groot.get_tvd(train2, zone)

    return (
        (tvd1.split("->")[0] == tvd2.split("->")[1])
        and
        (tvd1.split("->")[1] == tvd2.split("->")[0])
    )


def is_a_divergence(groot: Groot, tvd: str) -> bool:

    parents = list(groot.tvds_graph.predecessors(tvd))
    if not parents:
        return False
    siblings = list(groot.tvds_graph.successors(parents[0]))
    return len(siblings) == 2


def is_a_convergence(groot: Groot, tvd: str) -> bool:

    children = list(groot.tvds_graph.successors(tvd))
    if not children:
        return False
    siblings = list(groot.tvds_graph.predecessors(children[0]))
    return len(siblings) == 2
