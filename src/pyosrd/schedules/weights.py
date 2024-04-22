import pandas as pd

from pyosrd import OSRD

from .from_osrd import _step_is_a_station, step_type


def _zone_from_train_and_station(
    osrd: OSRD,
    train: int | str,
    station: str,
) -> str | None:

    if isinstance(train, str):
        train = osrd.trains.index(train)

    return next((
        key
        for key, value in osrd.stop_positions[train].items()
        if 'id' in value and value['id'] == station
    ), None)


def stations_only(osrd: OSRD) -> pd.DataFrame:
    """Creates a zone weight df where station have weight 1 and other zones 0

    Parameters
    ----------
    osrd : OSRD
        OSRD simulation object

    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule
    """
    return _step_is_a_station(osrd).astype(int)


def all_steps(osrd: OSRD) -> pd.DataFrame:
    """Creates a zone weight df where all the steps have weight=1

    Parameters
    ----------
    osrd : OSRD
        OSRD simulation object


    Returns
    -------
    pd.DataFrame
        DataFrame with the same shape as a schedule
    """
    return step_type(osrd).notna().astype(int)


@pd.api.extensions.register_dataframe_accessor("weights")
class Weights:

    def __init__(osrd, pandas_obj):
        osrd._obj = pandas_obj

    def train(osrd, train: int | str, value: int):

        if isinstance(train, int):
            train = osrd._obj.columns[train]

        osrd._obj[train] = (
            osrd._obj[train]
            .apply(
                lambda x: 0 if x == 0 else value
            )
        )

    def train_zone(osrd, train: int | str, zone: str, value: int):

        if isinstance(train, int):
            train = osrd._obj.columns[train]

        osrd._obj.loc[zone, train] = value

    def train_station_sim(
        osrd,
        train: int | str,
        station: str,
        value: int,
        sim: OSRD,
    ):

        if isinstance(train, int):
            train = osrd._obj.columns[train]

        zone = _zone_from_train_and_station(sim, train, station)
        if zone is not None:
            osrd.train_zone(train, zone, value)
