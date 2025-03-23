import itertools
import math
from .groot import Groot


def difference_durations(g1: Groot, g2: Groot) -> dict[str, dict[str, float]]:

    diff = dict()

    for train, times in g1.times.items():
        for tvd, t in times.items():
            if tvd in g2.times[train]:
                d1 = g2.times[train][tvd][1]-g2.times[train][tvd][0]
                d2 = t[1] - t[0]
                if not math.isclose(d1, d2):
                    if train not in diff:
                        diff[train] = dict()
                    diff[train][tvd] = round(d2 - d1, 0)

    return diff


def difference_departures_per_zone(
        g1: Groot,
        g2: Groot
) -> dict[str, dict[str, float]]:
    """ Compute the differences of departure times of all
    zones. Only compute difference if the zone is present in
    both groot.

    Parameters
    ----------
    g1 : Groot
        groot to be used as the left hand side of the
        differences computation
    g2 : Groot
        groot to be used as the left hand side of the
        differences computation

    Returns
    -------
    dict[str, dict[str, float]]
        A dictionnary of all differences in departure time per zone
        per train. Access of the dictionnary is done by
        dict[train][zone] = difference in departure
        time of the zone
    """
    diff = dict()

    for train, times in g1.times.items():
        for tvd, t in times.items():
            if tvd in g2.times[train]:
                d1 = g2.times[train][tvd][1]
                d2 = t[1]
                if train not in diff:
                    diff[train] = dict()
                diff[train][tvd] = round(d2 - d1, 0)

    return diff


def difference_departures(g1: Groot, g2: Groot) -> dict[str, float]:

    diff = dict()

    for train in g1.times:
        tvd = g1.path(train)[0]
        if (
            tvd == g2.path(train)[0]
            and not math.isclose(g1.times[train][tvd][0], g2.times[train][tvd][0])
        ):
            diff[train] = g2.times[train][tvd][0] - g1.times[train][tvd][0]
    return diff


def rerouted_paths(g: Groot, ref: Groot) -> dict[str, list[list[str]]]:

    rerouted = dict()

    for train in g.trains:
        new_tvds = [tvd if tvd not in ref.path(train) else None for tvd in g.path(train) ]

        new_paths = [
            list(v)
            for k, v in itertools.groupby(new_tvds, key=lambda x: x is None)
            if not k
        ]

        if new_paths:
            rerouted[train] = new_paths

    return rerouted


def updated_paths(g1: Groot, g2: Groot) -> dict[str, list[str]]:

    diff = dict()

    for train in g1.times:
        if (path1 := g1.path(train)) != g2.path(train):
            diff[train] = path1

    return diff
