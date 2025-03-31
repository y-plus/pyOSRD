from ..groot import Groot, GrootTimes
from .rerouting import reroute_train_to_avoid_zone
from .solve_conflict import solve_conflict


def evaluate_action(
    groot: Groot,
    ref: Groot,
    action: str,
    not_before: float = 0
) -> GrootTimes | None:
    match action:
        case 'R':
            tr1, tr2, zone, _ = groot.earliest_conflict()
            try:
                train_to_reroute = ref.trains_order_in_zone(tr1, tr2, zone)[1]
            except KeyError:
                train_to_reroute = groot.trains_order_in_zone(tr1, tr2, zone)[1]
            
            original_times = reroute_train_to_avoid_zone(
                groot,
                train_to_reroute,
                zone,
            )
        case 'S':
            original_times = solve_conflict(
                groot,
                ref=ref,
                reorder=False,
                not_before=not_before,
            )
        case 'O':
            original_times = solve_conflict(
                groot,
                ref=ref,
                reorder=True,
                not_before=not_before,
            )
        case _:
            return
    return original_times