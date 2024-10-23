from pyosrd import OSRD


def _route_tvds(
    sim: OSRD,
    zones: dict[str, str],
    route_id: str
) -> list[str]:

    if not hasattr(sim, 'tvd_limits'):
        sim.tvd_limits = set()
        for z in zones:
            sim.tvd_limits.update(z.split('->'))

    route = next(r for r in sim.infra['routes'] if r['id']==route_id)
    detectors = [d for d in route['release_detectors'] if d in sim.tvd_limits]

    tvds = []
    in_ = route['entry_point']['id']

    while in_:
        tvd = next(
            (
                z for z in zones
                if z.split('->')[0] == in_ and z.split('->')[1] in detectors
            ),
            None
        )
        if tvd:
            tvds.append(tvd)
            in_ = tvd.split('->')[1]
        else:
            tvds.append(
                '->'.join([in_, route['exit_point']['id']])
            )
            in_=None

    return tvds


def get_times_and_lengths(
    sim: OSRD,
    zones: dict[str, str],
) -> tuple[
    dict[str, dict[str, tuple[float, float]]],
    dict[str, dict[str, float]],
    dict[str, float],
]:

    times = dict()
    min_durations = dict()
    lengths = dict()
    for train in sim.trains:
        times[train] = dict()
        min_durations[train] = dict()
        train_points = sim.points_encountered_by_train(
            train,
            types=['detector', 'departure', 'arrival']
        )
        points = {d['id']: d for d in train_points}
        routes = sim.train_routes(train)
        for route_id in routes:
            tvds = _route_tvds(sim, zones, route_id)
            for tvd in tvds:
                d_in, d_out = tvd.split('->')
                if d_in not in points:
                    d_in = f"departure_{train}"
                if d_out not in points:
                    d_out = f"arrival_{train}"
                if 't_eco' in points[d_in]:
                    times[train][tvd] = (
                        points[d_in]['t_eco'],
                        points[d_out]['t_tail_eco']
                    )
                else:
                    times[train][tvd] = (
                        points[d_in]['t_base'],
                        points[d_out]['t_tail_base']
                    )
                min_durations[train][tvd] = (
                    points[d_out]['t_tail_base']
                    - points[d_in]['t_base']
                )
                lengths[tvd] = (
                    points[d_out]['offset']
                    - points[d_in]['offset']
                )
    return times, min_durations, lengths