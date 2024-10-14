import copy

import networkx as nx
import numpy as np
import pandas as pd

from pyosrd import OSRD
from pyosrd.schedules import Schedule


def step_has_fixed_duration(sim: OSRD) -> pd.DataFrame:
    """Have the steps a fixed duration ?

    Generates a DataFrame with the same shape as a schedule

    For a given cell:
    - row (=index) is the zone
    - column is the rain index
    - value
      - True = the step duration can not be modified because the
        zone contains switch elements
      - False = the zone is either a block or a station lane.
        The duration can be modified,
        ie the train can stay longer in this zone.
      - NaN = the step does not exist, ie
        the zone is not in the train's path

    Parameters
    ----------
    sim : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule.
    """
    return (
        pd.concat(
            [
                pd.DataFrame(sim.stop_positions[col]).T.id.isna()
                for col, _ in enumerate(sim.trains)
            ],
            axis=1
        )
        .set_axis(sim.trains, axis=1)
        .reindex(_schedule_dfs_from_OSRD(sim)[0].index)
    )


def step_type(
    sim: OSRD,
    s: Schedule | None = None,
    points_encountered_by_trains: dict[str, list] | None = None,
) -> pd.DataFrame:
    """Is the zone a switch, a station lane or a block with a signal ?

    Generates a DataFrame with the same shape as a schedule

    For a given cell:
    - row (=index) is the zone
    - column is the train index
    - value
      - 'station', "signal' or 'switch'
      - NaN = the step does not exist, ie
        the zone is not in the train's path

    Parameters
    ----------
    sim : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule.
    """

    if s is None:
        s = schedule_from_osrd(sim)

    if points_encountered_by_trains is None:
        points_encountered_by_trains = {
            train: sim.points_encountered_by_train(train)
            for train in sim.trains
        }

    st = pd.DataFrame(columns=s.trains, index=s.zones)

    for train in s.trains:
        p = [
            point['id']
            for point in points_encountered_by_trains[train]
            if point['type'] in ['station', 'detector']
        ]
        for z in s.path(train):
            if '<->' in z:
                A, B = z.split('<->')
                idxA = p.index(A) if A in p else None
                idxB = p.index(B) if B in p else None

                points = p[idxA:idxB] if p[idxA:idxB] else p[idxB:idxA]
                if len(points) > 1 and points != p:
                    st.loc[z, train] = 'station'
                elif s.path(train)[-1] == z:
                    st.loc[z, train] = 'last_zone'
                else:
                    st.loc[z, train] = 'signal'
            else:
                st.loc[z, train] = 'switch'
    return st


def _step_is_a_station(sim: OSRD) -> pd.DataFrame:
    return step_type(sim, schedule_from_osrd(sim)) == 'station'


def step_station_id(sim: OSRD) -> pd.DataFrame:
    """Label of the station when the zone is a station lane

    Parameters
    ----------
    sim : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule.
    """
    return (
        _step_is_a_station(sim) * (
            pd.concat(
                [
                    pd.DataFrame(sim.stop_positions[col]).T.id
                    for col, _ in enumerate(sim.trains)
                ],
                axis=1
            )
            .set_axis(sim.trains, axis=1)
            .reindex(_schedule_dfs_from_OSRD(sim)[0].index)
        )
    ).replace('', np.nan)


def _schedule_dfs_from_OSRD(
    sim: OSRD,
    eco_or_base: str = 'base',
    delayed: bool = False,
    points_encountered_by_trains: dict[str, list] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None]:

    if points_encountered_by_trains is None:
        points_encountered_by_trains = {
            train: sim.points_encountered_by_train(train)
            for train in sim.trains
        }

    # STEP 1: CREATE DATAFRAME
    # index USING ZONES FROM INFRASTRUCTURE
    # columns USING TRAINS FROM SIMULATION

    tvd_zones = sim.tvd_zones

    min_times = pd.DataFrame(
        columns=pd.MultiIndex.from_product(
            [sim.trains, ['s', 'e']]
        ),
        index=list(dict.fromkeys(tvd_zones.values()))
    )
    min_times_dict = {train: {'s': {}, 'e': {}} for train in sim.trains}

    if eco_or_base == 'eco':
        df = min_times.copy()
        df_dict = {train: {'s': {}, 'e': {}} for train in sim.trains}

    if delayed:
        sim_d = sim.delayed()
        df_delayed = min_times.copy(deep=True)
        delayed_dict = {train: {'s': {}, 'e': {}} for train in sim.trains}

    # STEP2: LOOP ON TRAINS IN RESULTS TO FILL IN START & END TIMES
    points_on_track_sections = sim.points_on_track_sections()

    for train in sim.trains:

        tvds_limits = []
        for track in sim.train_track_sections(train):
            elements = [
                p.id
                for p in points_on_track_sections[track['id']]
                if p.type in ['buffer_stop', 'detector']
            ]
            tvds_limits += (
                elements[::-1]
                if track['direction'] == 'STOP_TO_START'
                else elements
            )

        arrival_time_base = next(
            point['t_base']
            for point in points_encountered_by_trains[train]
            if point['type'] == 'arrival'
        )

        if eco_or_base == 'eco':
            arrival_time_eco = next(
                point['t_eco']
                for point in points_encountered_by_trains[train]
                if point['type'] == 'arrival'
            )

        if delayed:
            arrival_time_delayed = sim_d.points_encountered_by_train(
                train=train,
                types='arrival',
            )[0][f't_{eco_or_base}']

        detectors = [
            point
            for point in points_encountered_by_trains[train]
            if point['type'] == 'detector'
        ]
        if delayed:
            detectors_delayed = sim_d.points_encountered_by_train(
                train=train,
                types='detector',
            )

        first_detector = detectors[0]['id']
        last_detector = detectors[-1]['id']
        idx_first = tvds_limits.index(first_detector)
        idx_last = tvds_limits.index(last_detector)

        limits = tvds_limits[idx_first-1:idx_last+2]

        for i, _ in enumerate(limits[:-1]):

            start = limits[i]
            end = limits[i+1]
            joined = "<->".join(sorted([start, end]))
            zone = tvd_zones[joined]
            t_start = (
                sim.departure_times[sim.trains.index(train)]
                if i == 0
                else [
                    d['t_base']
                    for d in detectors
                    if d['id'] == start][0]
            )
            t_end = (
                arrival_time_base
                if i == len(limits)-2
                else [
                    d['t_tail_base']
                    for d in detectors
                    if d['id'] == end][0]
            )

            min_times_dict[train]['s'][zone] = t_start
            min_times_dict[train]['e'][zone] = t_end

            if eco_or_base == 'eco':
                t_start_eco = (
                    sim.departure_times[sim.trains.index(train)]
                    if i == 0
                    else [
                        d['t_eco']
                        for d in detectors
                        if d['id'] == start][0]
                )
                t_end_eco = (
                    arrival_time_eco
                    if i == len(limits)-2
                    else [
                        d['t_tail_eco']
                        for d in detectors
                        if d['id'] == end][0]
                )

                df_dict[train]['s'][zone] = t_start_eco
                df_dict[train]['e'][zone] = t_end_eco

            if delayed:
                t_start_delayed = (
                    sim_d.departure_times[sim_d.trains.index(train)]
                    if i == 0
                    else [
                        d[f't_{eco_or_base}']
                        for d in detectors_delayed
                        if d['id'] == start][0]
                )
                t_end_delayed = (
                    arrival_time_delayed
                    if i == len(limits)-2
                    else [
                        d[f't_tail_{eco_or_base}']
                        for d in detectors_delayed
                        if d['id'] == end][0]
                )
                delayed_dict[train]['s'][zone] = t_start_delayed
                delayed_dict[train]['e'][zone] = t_end_delayed

    # STEP 3: CLEAN UP
    for train in sim.trains:
        min_times[[(train, 's'), (train, 'e')]] =\
            pd.DataFrame(min_times_dict[train])

    min_times.index.name = None
    min_times.columns = pd.MultiIndex.from_product(
            [sim.trains, ['s', 'e']]
        )

    if eco_or_base == 'base':
        df = min_times.copy()
    else:
        for train in sim.trains:
            df[[(train, 's'), (train, 'e')]] =\
                pd.DataFrame(df_dict[train])

        df.index.name = None
        df.columns = pd.MultiIndex.from_product(
                [sim.trains, ['s', 'e']]
            )

    if not delayed:
        df_delayed = None
    else:
        for train in sim.trains:
            df_delayed[[(train, 's'), (train, 'e')]] =\
                pd.DataFrame(delayed_dict[train])

        df_delayed.index.name = None
        df_delayed.columns = pd.MultiIndex.from_product(
                [sim.trains, ['s', 'e']]
            )

    return df, min_times, df_delayed


def _merge_switch_zones(s: Schedule, _step_type: pd.DataFrame) -> Schedule:

    new_schedule = copy.copy(s)
    G = new_schedule.graph

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

            new_schedule.min_times.loc[
                merged_zone_name,
                (train, 's')
            ] = new_schedule.min_times.loc[switches, (train, 's')].min()
            new_schedule.min_times.loc[
                merged_zone_name,
                (train, 'e')
            ] = new_schedule.min_times.loc[switches, (train, 'e')].max()

            new_schedule._step_type.loc[merged_zone_name, train] = 'switch'

        new_schedule.df.drop(switches, inplace=True)
        new_schedule.min_times.drop(switches, inplace=True)
        new_schedule._step_type.drop(switches, inplace=True)

    return new_schedule


def schedule_from_osrd(
        sim: OSRD,
        delayed: bool = False,
) -> Schedule | tuple[Schedule, Schedule]:
    """Construct schedule objects  from OSRD simulations

    If `delayed==True`, returns a tuple of schedules: one for the ref
    simulation and one for the delayed simulation

    Additional informations are created as attributes
    - _trains: list of train labels
    - _step_type
    - _min_times corresponding to base_simulations

    Parameters
    ----------
    case : OSRD
        OSRD simulation object
    delayed : bool, optional
        Also return the delayed schedule ?, by default False

    Returns
    -------
    Schedule | tuple[Schedule, Schedule]
    """

    s = Schedule(len(sim.routes), sim.num_trains)
    s._trains = sim.trains

    if delayed:
        s_delayed = Schedule(len(sim.routes), sim.num_trains)
        s_delayed._trains = sim.trains

    group, idx = sim._train_schedule_group[sim.trains[0]]
    if sim.results[group]['eco_simulations'][idx]:
        eco_or_base = 'eco'
    else:
        eco_or_base = 'base'

    points_encountered_by_trains = {
        train: sim.points_encountered_by_train(train)
        for train in sim.trains
    }

    s._df, s._min_times, delayed_df = _schedule_dfs_from_OSRD(
        sim,
        eco_or_base,
        delayed=delayed,
        points_encountered_by_trains=points_encountered_by_trains
    )
    s._step_type = step_type(sim, s, points_encountered_by_trains)

    if delayed:
        s_delayed._df = delayed_df
        s_delayed._min_times = s._min_times.copy()
        s_delayed._step_type = s._step_type.copy()

    s = _merge_switch_zones(s, s._step_type)

    if delayed:
        s_delayed = _merge_switch_zones(s_delayed, s_delayed._step_type)

    if not delayed:
        return s
    return s, s_delayed
