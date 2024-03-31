"""Helper fuctions to deal with intervals and overlaps

An interval = a tuple of two floats

"""


def intersections(
    intervals: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    """intersections between a list of open intervals

    An interval is represented by a tuple of floats (start, end)

    Arguments
    ---------
    intervals:  list[tuple[float, float]]
        list of intervals

    Returns
    -------
    list[tuple[float, float]]
        list of intersections

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


def overlapping(
    intervals: list[tuple[float, float]]
) -> dict[tuple[int, int]: tuple[float, float]]:

    sorted = intervals.copy()
    sorted.sort(key=lambda x: x[0])

    no_overlap_order = []
    for i, interval in enumerate(sorted):
        no_overlap_order.append((i, interval[0]))
        no_overlap_order.append((i, interval[1]))

    actual_order = no_overlap_order.copy()
    actual_order.sort(key=lambda x: x[1])

    overlap_times = [
        actual
        for no_overlap, actual in zip(no_overlap_order, actual_order)
        if no_overlap != actual
    ]

    intersections = {
        (overlap_times[i-1][0], overlap_times[i][0]):
            (overlap_times[i-1][1], overlap_times[i][1])
        for i, _ in enumerate(overlap_times)
        if i % 2 != 0
    }

    return intersections
