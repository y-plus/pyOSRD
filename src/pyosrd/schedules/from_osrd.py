import copy

import networkx as nx
import numpy as np
import pandas as pd

from pyosrd import OSRD
from pyosrd.schedules import Schedule


def _schedule_df_from_OSRD(
    case: OSRD,
    eco_or_base: str = 'base',
) -> pd.DataFrame:

    # STEP 1: CREATE DATAFRAME
    # index USING ZONES FROM INFRASTRUCTURE
    # columns USING TRAINS FROM SIMULATION

    tvd_zones = case.tvd_zones
    df = pd.DataFrame(
        columns=pd.MultiIndex.from_product(
            [case.trains, ['s', 'e']]
        ),
        index=["<->".join(sorted(tvd)) for tvd in case._tvds]
    )
    df.insert(0, 'zone', tvd_zones.values())

    # STEP2: LOOP ON TRAINS IN RESULTS TO FILL IN START 1 END TIMES
    for train in case.trains:

        tvds_limits = []
        for track in case.train_track_sections(train):
            elements = [
                p.id
                for p in case.points_on_track_sections()[track['id']]
                if p.type in ['buffer_stop', 'detector']
            ]
            tvds_limits += (
                elements[::-1]
                if track['direction'] == 'STOP_TO_START'
                else elements
            )

        arrival_time = case.points_encountered_by_train(
            train=train,
            types='arrival',
        )[0][f't_{eco_or_base}']
        detectors = case.points_encountered_by_train(train, types='detector')
        first_detector = detectors[0]['id']
        last_detector = detectors[-1]['id']
        idx_first = tvds_limits.index(first_detector)
        idx_last = tvds_limits.index(last_detector)

        limits = tvds_limits[idx_first-1:idx_last+2]

        for i, _ in enumerate(limits[:-1]):

            start = limits[i]
            end = limits[i+1]

            t_start = (
                case.departure_times[case.trains.index(train)]
                if i == 0
                else [
                    d[f't_{eco_or_base}']
                    for d in detectors
                    if d['id'] == start][0]
            )
            t_end = (
                arrival_time
                if i == len(limits)-2
                else [
                    d[f't_tail_{eco_or_base}']
                    for d in detectors
                    if d['id'] == end][0]
            )
            joined = "<->".join(sorted([start, end]))
            name = tvd_zones[joined]
            df.loc[
                df.zone == name,
                train
            ] = (t_start, t_end)

    # STEP 3: CLEAN UP
    df.set_index('zone', inplace=True, drop=True)
    df.drop_duplicates(inplace=True)
    df.index.name = None
    df.columns = pd.MultiIndex.from_product(
            [case.trains, ['s', 'e']]
        )

    return df


def _merge_switch_zones(case: OSRD, s: Schedule) -> Schedule:
    print('*************\n')
    new_schedule = copy.copy(s)
    G = new_schedule.graph

    # Calculate zone_types
    _step_type = (pd.concat(
        [
            pd.DataFrame(case.stop_positions[col]).T.type
            for col, _ in enumerate(case.trains)
        ],
        axis=1
        )
        .set_axis(range(case.num_trains), axis=1)
        .reindex(s.df.index)
    )
    # Attach zone types as node attributes
    zone_type = (
        _step_type.T
        .agg(pd.unique)
        .apply(lambda x: [e for e in x if isinstance(e, str)])
        .apply(lambda x: x[0] if len(x) > 0 else np.nan)
    ).dropna().to_dict()
    nx.set_node_attributes(G, zone_type, 'type')

    # Keep only switch zones/nodes
    nodes = (
        node
        for node, data
        in G.nodes(data=True)
        if data.get("type") == "switch"
    )
    subgraph = G.subgraph(nodes)

    # Isolate groups of 2 or more consecutive switch nodes
    switch_groups = [
        list(s)
        for s in nx.connected_components(subgraph.to_undirected())
        if len(s) > 1
    ]

    for switches in switch_groups:
        merged_zone_name = "+".join(sorted(switches))

        for train in new_schedule.trains:
            new_schedule.df.loc[
                merged_zone_name,
                (train, 's')
            ] = new_schedule.df.loc[switches, (train, 's')].min()
            new_schedule.df.loc[
                merged_zone_name,
                (train, 'e')
            ] = new_schedule.df.loc[switches, (train, 'e')].max()

        new_schedule.df.drop(switches, inplace=True)
    return new_schedule


def schedule_from_osrd(
        case: OSRD,
        eco_or_base: str = 'base',
) -> Schedule:
    """Construct a schedule object  from an OSRD simulation

    Additional informations are created as attributes
    - _trains: list of train labels

    Parameters
    ----------
    case : OSRD
        OSRD simulation object
    eco_or_base : str, optional
        Base results or eco results ?, by default 'base'

    Returns
    -------
    Schedule
    """

    s = Schedule(len(case.routes), case.num_trains)
    s._df = _schedule_df_from_OSRD(case)
    s._trains = case.trains
    s = _merge_switch_zones(case, s)
    return s
