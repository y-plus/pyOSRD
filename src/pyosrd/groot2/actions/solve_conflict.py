import copy
from ..groot import Groot, GrootTimes
from ..exploitation.modifications import make_train_wait


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

def is_a_div(groot: Groot, tvd: str) -> bool:

    parents = list(groot.tvds_graph.predecessors(tvd))
    if not parents:
        return False
    brothers = list(groot.tvds_graph.successors(parents[0]))
    return len(brothers) == 2


def solve_conflict(
    groot: Groot,
    ref: Groot,
    switch_order: bool = False,
    leave_station_asap: bool = True,
    not_before: float = 0,
) -> GrootTimes | None:

    train1, train2, conflict_zone, t = groot.earliest_conflict()

    if not conflict_zone:
        return groot

    try:
        priority_train, waiting_train = ref.trains_order_in_zone(
            train1,
            train2,
            conflict_zone
        )
    except KeyError:    
        priority_train, waiting_train = groot.trains_order_in_zone(
            train1,
            train2,
            conflict_zone
        )

    opposite_directions = head_to_head(groot, priority_train, waiting_train, conflict_zone)

    can_switch = (
        groot.previous_common_convergence(train1, train2, conflict_zone)
    )

    if switch_order and (not can_switch) and not opposite_directions:
        return None
   
    if switch_order:
        priority_train, waiting_train = waiting_train, priority_train

    if groot.ends_with_a_signal[
        groot.get_tvd(priority_train, conflict_zone)
    ]:
        idx_conflict = groot.path_zones(priority_train).index(conflict_zone)
    else:
        idx_conflict = groot.path_zones(priority_train).index(
            groot.next_signal(priority_train, conflict_zone)
        )

    common_zones = []
    for zone in groot.path_zones(priority_train)[idx_conflict:]:
        if (
            zone in groot.path_zones(waiting_train)
            and not is_a_div(groot, groot.get_tvd(priority_train, zone))
        ):
            common_zones.append(zone)
        else:
            break

    if not common_zones:
        zone_to_free = conflict_zone
    else:
        zone_to_free = common_zones[-1]


    prev_station = groot.previous_station(waiting_train, zone_to_free)
    if prev_station is None:
        prev_station = groot.path_zones(waiting_train)[0]
    if prev_station == conflict_zone:
        prev_station = (
            groot.previous_station(waiting_train, prev_station)
            if prev_station != groot.path_zones(waiting_train)[0]
            else prev_station
        )
        leave_station_asap = False

    
    if groot.times_zones[waiting_train][prev_station][1] < not_before:
        return
    
    if leave_station_asap and not opposite_directions:

        modified_times = {waiting_train: copy.deepcopy(groot.times[waiting_train])}

        conflict_in_common_zones = True
        while conflict_in_common_zones:
            
            make_train_wait(
                groot,
                waiting_train,
                priority_train,
                groot.previous_signal(waiting_train, conflict_zone),
                conflict_zone,
            )
            
            tr1, tr2 , conflict_zone, _ = groot.earliest_conflict()
            conflict_in_common_zones = (
                set([tr1, tr2]) == set([priority_train, waiting_train])
                and conflict_zone in common_zones
            )

        return modified_times
    
    return make_train_wait(
            groot,
            waiting_train,
            priority_train,
            prev_station,
            zone_to_free,
        )
