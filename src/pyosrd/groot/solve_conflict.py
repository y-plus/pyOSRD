import copy
from pyosrd.groot import Groot

def head_to_head(
    self: Groot,
    train1: str,
    train2: str,
    zone: str
) -> bool:
    tvd1 = self.get_tvd(train1, zone)
    tvd2 = self.get_tvd(train2, zone)

    return (
        (tvd1.split("->")[0] == tvd2.split("->")[1])
        and
        (tvd1.split("->")[1] == tvd2.split("->")[0])
    )

def is_a_div(self: Groot, tvd: str) -> bool:

    parents = list(self.tvds_graph.predecessors(tvd))
    if not parents:
        return False
    siblings = list(self.tvds_graph.successors(parents[0]))
    return len(siblings) == 2


def solve_conflict(
    self: Groot,
    ref: Groot,
    switch_order: bool = False,
    leave_station_asap: bool = True,
    not_before: float = 0,
    saved_times: list[dict[str, str|float]] | None = None,
    in_place: bool=False,
) -> Groot | None:

    if saved_times is not None:
        saved_times.append(copy.deepcopy(self.times))

    train1, train2, conflict_zone, t = self.earliest_conflict()

    if not conflict_zone:
        return self

    try:
        priority_train, waiting_train = ref.trains_order_in_zone(
            train1,
            train2,
            conflict_zone
        )
    except KeyError:    
        priority_train, waiting_train = self.trains_order_in_zone(
            train1,
            train2,
            conflict_zone
        )

    opposite_directions = head_to_head(self, priority_train, waiting_train, conflict_zone)

    can_switch = (
        self.previous_common_convergence(train1, train2, conflict_zone)
        # or
        # self.path(train1)[0] == self.path(train2)[0]
    )

    if switch_order and (not can_switch) and not opposite_directions:
        return None
   
    if switch_order:
        priority_train, waiting_train = waiting_train, priority_train

    if self.ends_with_a_signal[
        self.get_tvd(priority_train, conflict_zone)
    ]:
        idx_conflict = self.path_zones(priority_train).index(conflict_zone)
    else:
        idx_conflict = self.path_zones(priority_train).index(
            self.next_signal(priority_train, conflict_zone)
        )

    common_zones = []
    for zone in self.path_zones(priority_train)[idx_conflict:]:
        if (
            zone in self.path_zones(waiting_train)
            # and self.ends_with_a_signal[self.get_tvd(priority_train, zone)]
            and not is_a_div(self, self.get_tvd(priority_train, zone))
        ):
            common_zones.append(zone)
        else:
            break

    if not common_zones:
        zone_to_free = conflict_zone
    else:
        zone_to_free = common_zones[-1]


    prev_station = self.previous_station(waiting_train, zone_to_free)
    if prev_station is None:
        prev_station = self.path_zones(waiting_train)[0]
    if prev_station == conflict_zone:
        prev_station = (
            self.previous_station(waiting_train, prev_station)
            if prev_station != self.path_zones(waiting_train)[0]
            else prev_station
        )
        leave_station_asap = False

    if in_place:
        new_groot = self
    else:
        new_groot = copy.deepcopy(self)
    new_groot._times_zones = None

    if self.times_zones[waiting_train][prev_station][1] < not_before:
        new_groot.times = {}
        if in_place:
            return
        else:
            return new_groot
    
    if opposite_directions:
        leave_station_asap = False

    if leave_station_asap:

        conflict_in_common_zones = True

        while conflict_in_common_zones:
            
            if in_place:
                new_groot.make_train_wait(
                    waiting_train,
                    priority_train,
                    new_groot.previous_signal(waiting_train, conflict_zone),
                    conflict_zone,
                    in_place=True
                )
            else:
                new_groot = new_groot.make_train_wait(
                    waiting_train,
                    priority_train,
                    new_groot.previous_signal(waiting_train, conflict_zone),
                    conflict_zone
                )
            tr1, tr2 , conflict_zone, _ = new_groot.earliest_conflict()
            conflict_in_common_zones = (
                set([tr1, tr2]) == set([priority_train, waiting_train])
                and conflict_zone in common_zones
            )
    else:
        if in_place:
            new_groot.make_train_wait(
                waiting_train,
                priority_train,
                prev_station,
                zone_to_free,
                in_place=True
            )
            
        else:
            new_groot = new_groot.make_train_wait(
                waiting_train,
                priority_train,
                prev_station,
                zone_to_free
            )

    if not in_place:
        return new_groot