import numpy as np
import plotly.graph_objects as go

from pyosrd.utils import seconds_to_hour, hour_to_seconds
from pyosrd.groot import Groot
from pyosrd.groot.compare import difference_departures_per_zone


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
        time for train_dict in data.values() for time in train_dict.keys()
    ]
    entries.sort()
    return entries


def interpolate_entries(
    data: dict[str, dict[float, float]],
    entries: list[float],
    all_trains: bool
) -> dict[str, dict[float, float]]:
    """_summary_

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
        new_data[train] = np.interp(
            entries,
            keys,
            values,
            None if all_trains else 0,
            None if all_trains else 0
        )

    return new_data


def build_dict_difference_departures_per_departure_times(
        groot: Groot,
        diff: dict[str, dict[str, float]]
) -> dict[str, dict[str, float]]:
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

    Returns
    -------
    dict[str, dict[str, float]]
        A dictionnary of all differences in departure time per
        departure time per train. Access of the dictionnary is done by
        dict[train][departure_time] = difference in departure
        time of the zone (corresponding to the departure time).
    """
    result = {}
    for train in diff.keys():
        train_dict = diff[train]
        result[train] = {}
        for tvd in train_dict.keys():
            departure_time = groot.times[train][tvd][1]
            result[train][departure_time] = diff[train][tvd]

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
    if len(non_zero_entries) == 0:
        return -1
    return non_zero_entries[-1]


def get_latest_non_zero_delay(
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


def plot_groot_delays(
    disrupted: Groot,
    ref: Groot,
    all_trains: bool = True
) -> go.Figure:
    """Build a figure showing the cumulated delay of the disrupted groot

    Parameters
    ----------
    disrupted : Groot
        The disrupted or dispatched groot.
    ref : Groot
        THe reference groot.
    all_trains : bool
        true if we want to keep delays for all trains or only for
        trains active at each time point (delay will end at 0 if false)

    Returns
    -------
    go.Figure
        A figure showing the cumulated delays of the disrupted groot.
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
    all_entries = merge_time_entries(diff_departure_time_per_dep_time)
    new_data = interpolate_entries(
        diff_departure_time_per_dep_time,
        all_entries,
        all_trains
    )

    time = all_entries
    delays = new_data
    latest_non_zero_delays = get_latest_non_zero_delay(
        diff_departure_time_per_dep_time
    )
    keys = [
        k for k, _ in sorted(
            latest_non_zero_delays.items(),
            reverse=not all_trains,
            key=lambda item: item[1]
        )
    ]

    if not all_trains:
        time = [t for t in time if t < max(
            [val for _, val in latest_non_zero_delays.items()]
        )]

    fig = go.Figure(
        data=[
            go.Scatter(
                name=train,
                x=time,
                y=delays[train],
                stackgroup='Delays'
            )
            for train in keys
            if sum(delays[train]) > 0
        ],
        layout={
                "title": 'Cumulated delays over time'
                if all_trains
                else 'Active delays over time',
                "template": "simple_white",
                "hovermode": "x unified"
            },
    )
    if not fig.data:
        return fig

    xmax = round(max(time))
    xticks = list(range(0, xmax + xmax // 5, xmax // 5))
    ymax = int(sum(max(v) for v in delays.values())) + 1
    yticks = list(range(0, ymax + ymax // 5, ymax // 5))

    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=yticks,
            ticktext=[seconds_to_hour(ytick) for ytick in yticks]
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=xticks,
            ticktext=[seconds_to_hour(xtick) for xtick in xticks]
        )
    )
    return fig
