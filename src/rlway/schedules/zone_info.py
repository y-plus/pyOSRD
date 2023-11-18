import numpy as np
import pandas as pd

from rlway.pyosrd import OSRD
from . import schedule_from_osrd


def step_has_fixed_duration(osrd: OSRD) -> pd.DataFrame:
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
        the zone is not in the train's trajectory

    Parameters
    ----------
    osrd : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule.
    """
    return (
        pd.concat(
            [
                pd.DataFrame(osrd.stop_positions[col]).T.id.isna()
                for col, _ in enumerate(osrd.trains)
            ],
            axis=1
        )
        .set_axis(range(2), axis=1)
        .reindex(schedule_from_osrd(osrd).df.index)
    )


def step_type(osrd: OSRD) -> pd.DataFrame:
    """Is the zone a switch, a station lane or a block with a signal ?

    Generates a DataFrame with the same shape as a schedule

    For a given cell:
    - row (=index) is the zone
    - column is the rain index
    - value
      - 'station', "signal' or 'switch'
      - NaN = the step does not exist, ie
        the zone is not in the train's trajectory

    Parameters
    ----------
    osrd : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule.
    """
    return (
        pd.concat(
            [
                pd.DataFrame(osrd.stop_positions[col]).T.type
                for col, _ in enumerate(osrd.trains)
            ],
            axis=1
        )
        .set_axis(range(2), axis=1)
        .reindex(schedule_from_osrd(osrd).df.index)
    )


def _step_is_a_station(osrd: OSRD) -> pd.DataFrame:
    return step_type(osrd) == 'station'


def step_station_id(osrd: OSRD) -> pd.DataFrame:
    """Label of the station when the zone is a station lane

    Parameters
    ----------
    osrd : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule.
    """
    return (
        _step_is_a_station(osrd) * (
            pd.concat(
                [
                    pd.DataFrame(osrd.stop_positions[col]).T.id
                    for col, _ in enumerate(osrd.trains)
                ],
                axis=1
            )
            .set_axis(range(2), axis=1)
            .reindex(schedule_from_osrd(osrd).df.index)
        )
    ).replace('', np.nan)
