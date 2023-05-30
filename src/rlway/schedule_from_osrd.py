from typing import Dict, List

import pandas as pd

from rlway.schedules import Schedule


def schedule_from_simulation(
        infra: Dict,
        res: List,
        simplify_route_names: bool = False,
) -> Schedule:

    routes = [
        route['id']
        for route in [infra['routes']]
    ]

    s = Schedule(len(routes), len(res))

    routes_switches = {
        route['id']: list(route['switches_directions'].keys())[0]
        for route in [infra['routes']]
        if len(list(route['switches_directions'].keys())) != 0
    }
    simulations = 'base_simulations'
    simulations = 'eco_simulations'

    for train in range(s.num_trains):
        route_occupancies = res[train][simulations][0]['route_occupancies']
        for route, times in route_occupancies.items():
            if route in routes:
                idx = routes.index(route)
                s._df.loc[idx, (train, 's')] = times['time_head_occupy']
                s._df.loc[idx, (train, 'e')] = times['time_tail_free']
    s._df.index = routes

    s._df.index = (
        pd.Series(s.df.index.map(routes_switches))
        .fillna(pd.Series(s.df.index))
    )

    s._df = s.df[~s.df.index.duplicated()]

    if simplify_route_names:
        s._df.index = (
            s.df.index
            .str.replace('rt.', '', regex=False)
            .str.replace('buffer_stop', 'STOP', regex=False)
        )

    return s
