import math
from pyosrd.groot import Groot


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
                    diff[train][tvd] = (round(d2 - d1, 0))

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


def difference_path(g1: Groot, g2: Groot) -> dict[str, dict[str, float]]:
    ...
