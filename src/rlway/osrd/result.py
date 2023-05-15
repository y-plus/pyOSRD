from typing import Dict, List, Tuple

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes

from rlway.osrd.infra import points_on_track_sections, track_section_lengths
from rlway.osrd.simulation import trains


def train_track_sections(result: Dict, train: int) -> List[str]:
    """List of tracks during train trajectory"""

    return list(
        dict.fromkeys([
            time["track_section"]
            for time in result[train]['base_simulations'][0]['head_positions']
        ]))


def encountered_points_by_train(
    infra: Dict,
    result: Dict,
    train: int,
    types: List[str] = [
        'signal',
        'detector',
        'cvg_signal',
        'station',
    ]
) -> List[Tuple[str, str, float, float, float]]:
    """Points encountered by a train during its trajectory

    Parameters
    ----------
    infra : Dict
    result : Dict
    train : int
    types : List[str], optional
        Types of points, by default
        ['signal', 'detector', 'cvg_signal', 'station']

    Returns
    -------
    List[Tuple[str, str, float, float, float]]
        Points encountered (label, type, offset, t_min, t)
    """

    lengths = [
        track_section_lengths(infra)[ts]
        for ts in train_track_sections(result, 0)
    ]

    track_offsets = [
        sum(lengths[: i]) for i, _ in enumerate(lengths)
    ]

    records_min = result[1]['base_simulations'][0]['head_positions']
    offset = records_min[0]['offset']
    offsets_min = [offset + t['path_offset'] for t in records_min]
    t_min = [t['time'] for t in records_min]

    records_eco = result[1]['eco_simulations'][0]['head_positions']
    offsets_eco = [offset + t['path_offset'] for t in records_eco]
    t = [t['time'] for t in records_eco]

    points = []
    for i, ts in enumerate(train_track_sections(result, train)):
        points += [{
            'id': pt,
            'type': tag,
            'offset': pos + track_offsets[i],
            't_min': np.interp(
                [pos + track_offsets[i]],
                offsets_min,
                t_min
            ).item(),
            't': np.interp([pos + track_offsets[i]], offsets_eco, t).item(),
            }
            for pt, (pos, tag) in points_on_track_sections(infra)[ts].items()
            if tag in types
        ]

    return points


def space_time_graph(
    infra: Dict,
    simulation: List,
    result: Dict,
    train: int,
    eco_or_base: str = 'eco',
    show: List[str] = ['station', 'cvg_signal'],
) -> Axes:

    _, ax = plt.subplots()

    points = encountered_points_by_train(
        infra,
        result,
        train,
        show
    )

    records_min = \
        result[train][eco_or_base+'_simulations'][0]['head_positions']
    offset = records_min[0]['offset']
    offsets = [offset + t['path_offset'] for t in records_min]
    times = [t['time']/60 for t in records_min]

    ax.plot(
        times,
        offsets,
    )
    for point in points:
        ax.axhline(point['offset'], color='k', linestyle=':');  # noqa

    ax.set_yticks(
        [point['offset'] for point in points],
        [point['id'] for point in points]
    );  # noqa

    ax.set_title(
        trains(simulation)[train]
        + f" ({eco_or_base})"
    );  # noqa

    return ax
