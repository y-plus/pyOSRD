import pandas as pd

from pyosrd import OSRD
from pyosrd.schedules import Schedule


def schedule_df_from_OSRD(
    case: OSRD,
    eco_or_base: str = 'base',
) -> pd.DataFrame:

    tvd_zones = case.tvd_zones
    df = pd.DataFrame(
        columns=pd.MultiIndex.from_product(
            [range(case.num_trains), ['s', 'e']]
        ),
        index=["<->".join(sorted(tvd)) for tvd in case._tvds]
    )
    df.insert(0, 'block', tvd_zones.values())
    for train, _ in enumerate(case.trains):

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
                case.departure_times[train]
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
                df.block == name,
                train
            ] = (t_start, t_end)

    df.set_index('block', inplace=True, drop=True)
    df.drop_duplicates(inplace=True)
    df.index.name = None
    df.columns = pd.MultiIndex.from_product(
            [range(case.num_trains), ['s', 'e']]
        )
    return df


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
    s._df = schedule_df_from_OSRD(case)
    s._trains = case.trains
    return s
