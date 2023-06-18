"""Helper fuctions to deal with intervals and overlaps

An interval =two floats

"""
from typing import Tuple, List


def intersections(
    intervals: List[Tuple[float, float]]
) -> List[Tuple[float, float]]:
    """intersections between a list of open intervals

    An interval is represented by a tuple of floats (start, end)

    Arguments
    ---------
    intervals:  List[Tuple[float, float]]
        Listt of intervals

    Returns
    -------
    List[Tuple[float, float]]
        List of intersections

    Examples
    --------
    >>> intersections([(0, 1), (0.5, 1.5)])
    [(0.5, 1)]
    >>> intersections([(0, 1), (1., 2.)])
    []
    >>> intersections([(0, 1), (2, 3), (2.5, 4)])
    [(2.5, 3)]
    """

    sorted = intervals.copy()
    sorted.sort(key=lambda x: x[0])

    no_overlap_order = []
    for i, interval in enumerate(sorted):
        no_overlap_order.append((i, interval[0]))
        no_overlap_order.append((i, interval[1]))

    actual_order = no_overlap_order.copy()
    actual_order.sort(key=lambda x: x[1])

    overlap_times = [
        actual[1]
        for no_overlap, actual in zip(no_overlap_order, actual_order)
        if no_overlap != actual
    ]

    intersections = [
        (overlap_times[i-1], overlap_times[i])
        for i, _ in enumerate(overlap_times)
        if i % 2 != 0
    ]

    return intersections
