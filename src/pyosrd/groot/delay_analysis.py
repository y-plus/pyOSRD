import numpy as np

from pyosrd.utils import hour_to_seconds, seconds_to_hour
from pyosrd.groot import Groot
from pyosrd.groot.compare import difference_departures_per_zone


def interpolate_entries(
    data: dict[str, dict[float, float]],
    entries: list[float],
    all_trains: bool
) -> dict[str, dict[float, float]]:
    """Interpolate all entries in the data dictionnary and
    the given entries. Usually the entries list will all
    the keys of the data dictionary merged.

    Parameters
    ----------
    data : dict[str, dict[float, float]]
        The dictionnary for every train and every time of
        derparture containing the difference between
        reference and dispatched groot.
    entries : list[float]
        the sorted list of all departure times.
    all_trains : bool
        true if we want to keep delays for all trains or only for
        trains active at each time point (delay will end at 0 if false)

    Returns
    -------
    dict
        The dictionnary for every train and every time of
        derparture containing the difference between
        reference and dispatched groot. With all difference
        interpolated for missing departure times.
    """
    new_data = {}
    for train, train_dict in data.items():
        keys = [k for k in train_dict.keys()]
        values = [v for v in train_dict.values()]
        interpolation = np.interp(
            entries,
            keys,
            values,
            None if all_trains else 0,
            None if all_trains else 0
        )
        new_data[train] = {
            entries[i]: interpolation[i] for i in range(0, len(interpolation))
        }

    return new_data


def merge_time_entries(data: dict[str, dict[float, float]]) -> list[float]:
    """Create a list of all time entries corresponding to the departure
    time of all zones for every train.

    Parameters
    ----------
    data : dict[str, dict[float, float]]
        The dictionnary for every train and every time of
        derparture containing the difference between
        reference and dispatched groot.

    Returns
    -------
    list[float]
        the sorted list of all departure times.
    """
    entries = [
        time
        for train_dict in data.values()
        for time in train_dict.keys()
    ]
    # important to avoid duplicated entries
    entries = list(set(entries))
    entries.sort()
    return entries


def build_dict_difference_departures_per_departure_times(
        groot: Groot,
        diff: dict[str, dict[str, float]],
        add_fictionnal_point_at_end: bool = False
) -> dict[str, dict[float, float]]:
    """Create a dictionnary storing the difference of departure time
    per departure time of each zone.

    Parameters
    ----------
    groot : Groot
        The groot to be used to get departure time from zones
    diff : dict[str, dict[str, float]]
        A dictionnary of all differences in departure time per zone
        per train. Access of the dictionnary is done by
        dict[train][zone] = difference in departure
        time of the zone. (from difference_departures_per_zone)
    add_fictionnal_point_at_end : bool
        If true a fictionnal time point will be added 1 second
        after the lasgt non null difference

    Returns
    -------
    dict[str, dict[float, float]]
        A dictionnary of all differences in departure time per
        departure time per train. Access of the dictionnary is done by
        dict[train][departure_time] = difference in departure
        time of the zone (corresponding to the departure time).
    """
    result = {}
    for train in diff.keys():
        train_dict = diff[train]
        train_diff = {}
        max_timestamp = -1
        for tvd in train_dict.keys():
            departure_time = groot.times[train][tvd][1]
            if diff[train][tvd] > 0:
                max_timestamp = max(max_timestamp, departure_time)
            train_diff[departure_time] = diff[train][tvd]

        if add_fictionnal_point_at_end and max_timestamp > 0:
            train_diff[max_timestamp+1] = 0
        result[train] = dict(sorted(train_diff.items()))

    return result


def get_groot_delays_timestamp(
    disrupted: Groot,
    ref: Groot,
    all_trains: bool,
    timestamp: str
) -> dict[str, float]:
    diff_departure_time_per_zone = difference_departures_per_zone(
        disrupted,
        ref
    )
    diff_departure_time_per_dep_time = \
        build_dict_difference_departures_per_departure_times(
            disrupted,
            diff_departure_time_per_zone
        )
    timestamp = hour_to_seconds(timestamp)
    all_entries = merge_time_entries(diff_departure_time_per_dep_time)
    all_entries.append(timestamp)
    all_entries.sort()
    new_data = interpolate_entries(
        diff_departure_time_per_dep_time,
        all_entries,
        all_trains
    )
    data_timestamp = {
        train: new_data[train][all_entries.index(timestamp)]
        for train in new_data.keys()
    }
    return data_timestamp


def latest_non_zero_timestamp(entries: dict[float, float]) -> float:
    """get the latest timestamp where
    the delay is non zero

    Parameters
    ----------
    entries : dict[float, float]
        the dictionnary containing the delay for each time stamp.

    Returns
    -------
    float
        the latest timestamp
    """
    non_zero_entries = [
        time
        for time, val in entries.items()
        if val > 0
    ]
    return -1 if len(non_zero_entries) == 0 else non_zero_entries[-1]


def get_latest_non_zero_delay_for_each_train(
    entries: dict[str, dict[float, float]]
) -> dict[str, float]:
    """get the latest timestamp where
    the delay is non zero for each train

    Parameters
    ----------
    entries : dict[str, dict[float, float]]
        the dictionnary containing the delay for each time stamp
        for each train.

    Returns
    -------
    dict[str, float]
        the latest timestamp for each train
    """
    return {
        train: latest_non_zero_timestamp(delays)
        for train, delays in entries.items()
        if latest_non_zero_timestamp(delays) > 0
    }


def earliest_non_zero_timestamp(entries: dict[float, float]) -> float:
    """get the earliest timestamp where
    the delay is non zero

    Parameters
    ----------
    entries : dict[float, float]
        the dictionnary containing the delay for each time stamp.

    Returns
    -------
    float
        the earliest timestamp
    """
    non_zero_entries = [
        time
        for time, val in entries.items()
        if val > 0
    ]
    return -1 if len(non_zero_entries) == 0 else non_zero_entries[0]


def get_earliest_non_zero_delay_for_each_train(
    entries: dict[str, dict[float, float]]
) -> dict[str, float]:
    """get the earliest timestamp where
    the delay is non zero for each train

    Parameters
    ----------
    entries : dict[str, dict[float, float]]
        the dictionnary containing the delay for each time stamp
        for each train.

    Returns
    -------
    dict[str, float]
        the earliest timestamp for each train
    """
    return {
        train: earliest_non_zero_timestamp(delays)
        for train, delays in entries.items()
        if earliest_non_zero_timestamp(delays) > 0
    }


def get_latest_non_zero_delay(
    disrupted: Groot,
    ref: Groot,
    seconds: bool = False,
) -> float :
    """ Get the latest non zero delay in seconds of the disrupted groot
    compared to the reference groot. This is the time after which all
    trains are back to a normal situation.

    Parameters
    ----------
    disrupted : Groot
        The disrupted groot to be analyzed.
    ref : Groot
        The reference groot to be used the analyze the disrupted one.
        The delays are computed comparing the two groots.

    Returns
    -------
    float
        The latest time where there is a delay in the disrupted groot.
        That time is given in seconds.
    """
    diff_departure_time_per_zone = difference_departures_per_zone(
        disrupted,
        ref
    )
    diff_departure_time_per_dep_time = \
        build_dict_difference_departures_per_departure_times(
            disrupted,
            diff_departure_time_per_zone
        )
    latest_non_zero_delays = get_latest_non_zero_delay_for_each_train(
        diff_departure_time_per_dep_time
    )

    time = max(
        [
            latest_non_zero_delay
            for latest_non_zero_delay in latest_non_zero_delays.values()
        ]
    )

    if seconds:
        return time
    return seconds_to_hour(time)