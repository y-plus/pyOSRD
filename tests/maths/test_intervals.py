from pyosrd.maths.intervals import intersections, overlapping


def test_interval_intersections():
    """cf test_interval_intersections.png"""

    fixed_intervals = [
        (1, 2),
        (3, 4),
        ]
    test_intervals = {
        (0, .5): [],
        (0, 1.5): [(1, 1.5)],
        (1.2, 1.8): [(1.2, 1.8)],
        (1.5, 2.5): [(1.5, 2)],
        (2.2, 2.8): [],
        (1.5, 3.5): [(1.5, 2), (3, 3.5)],
        (2.5, 3.5): [(3., 3.5)],
        (3.5, 3.8): [(3.5, 3.8)],
        (3.5, 4.5): [(3.5, 4)],
        (4.5, 5): [],
    }

    for interval, expected in test_intervals.items():
        assert intersections(fixed_intervals+[interval]) == expected


def test_interval_overlapping():
    """cf test_interval_intersections.png"""

    fixed_intervals = [
        (1, 2),
        (3, 4),
        ]
    test_intervals = {
        (0, .5): {},
        (0, 1.5): {(1, 0): (1, 1.5)},
        (1.2, 1.8): {(1, 1): (1.2, 1.8)},
        (1.5, 2.5): {(1, 0): (1.5, 2)},
        (2.2, 2.8): {},
        (1.5, 3.5): {(1, 0): (1.5, 2), (2, 1): (3, 3.5)},
        (2.5, 3.5): {(2, 1): (3., 3.5)},
        (3.5, 3.8): {(2, 2): (3.5, 3.8)},
        (3.5, 4.5): {(2, 1): (3.5, 4)},
        (4.5, 5): {},
    }

    for interval, expected in test_intervals.items():
        assert overlapping(fixed_intervals+[interval]) == expected
