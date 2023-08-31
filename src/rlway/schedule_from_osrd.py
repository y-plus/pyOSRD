import pandas as pd

from rlway.pyosrd import OSRD
from rlway.schedules import Schedule


def schedule_from_osrd(
        case: OSRD,
        simplify_route_names: bool = False,
        eco_or_base: str = 'base',
        fix_departures: bool = True,
) -> Schedule:

    s = Schedule(len(case.routes), case.num_trains)

    simulations = f'{eco_or_base}_simulations'

    for train in range(s.num_trains):
        group, idx = case._train_schedule_group[
            case.trains[train]
        ]
        route_occupancies = \
            case.results[group][simulations][idx]['route_occupancies']
        for route, times in route_occupancies.items():
            if route in case.routes:
                idx = case.routes.index(route)
                s._df.loc[idx, (train, 's')] = times['time_head_occupy']
                s._df.loc[idx, (train, 'e')] = times['time_tail_free']
        if fix_departures:
            s._df.loc[:, (train, 's')] += case.departure_times[train]
            s._df.loc[:, (train, 'e')] += case.departure_times[train]
    s._df.index = case.routes

    s._df.index += '|'+(
        pd.Series(s.df.index.map(case.route_tvds))
        .fillna(pd.Series(s.df.index))
    )

    # s._df = s.df[~s.df.index.duplicated()]

    if simplify_route_names:
        s._df.index = (
            s.df.index
            .str.replace('rt.', '', regex=False)
            .str.replace('buffer_stop', 'STOP', regex=False)
        )

    return s
