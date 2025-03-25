import copy
from ..groot import Groot, GrootTimes
from ..exploitation.modifications import make_train_wait
from .utils import head_to_head, is_a_divergence

def solve_conflict(
    groot: Groot,
    ref: Groot,
    reorder: bool = False,
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

    can_reorder = (
        groot.previous_common_convergence(train1, train2, conflict_zone)
    )

    if reorder and (not can_reorder) and not opposite_directions:
        return None
   
    if reorder:
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
            and not is_a_divergence(groot, groot.get_tvd(priority_train, zone))
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

    if conflict_zone == groot.path_zones(waiting_train)[0]:
        leave_station_asap = False

    if groot.times_zones[waiting_train][prev_station][0] <= not_before and prev_station in groot.path_zones(priority_train):
        return
    
    if leave_station_asap and not opposite_directions:
        original_times = {waiting_train: copy.deepcopy(groot.times[waiting_train])}

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

        return original_times
    
    return make_train_wait(
            groot,
            waiting_train,
            priority_train,
            prev_station,
            zone_to_free,
        )
