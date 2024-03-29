
from pyosrd.schedules import Schedule


def test_schedules_trajectory(three_trains):
    assert three_trains.trajectory(0) == [0, 2, 3, 4]
    assert three_trains.trajectory(1) == [1, 2, 3, 5]
    assert three_trains.trajectory(2) == [0, 2, 3, 4]


def test_previous_zone(three_trains):
    assert three_trains.previous_zone(0, 0) is None
    assert three_trains.previous_zone(0, 2) == 0
    assert three_trains.previous_zone(0, 4) == 3


def test_next_zone(three_trains):
    assert three_trains.next_zone(0, 0) == 2
    assert three_trains.next_zone(0, 2) == 3
    assert three_trains.next_zone(0, 4) is None


def test_is_a_point_switch(two_trains):
    result = [
        two_trains.is_a_point_switch(0, 1, tr)
        for tr in two_trains.zones
    ]
    expected = [False, False, True, False, False, False]
    assert result == expected


def test_is_just_after_a_point_switch(two_trains):
    result = [
        two_trains.is_just_after_a_point_switch(0, 1, tr)
        for tr in two_trains.zones
    ]
    expected = [False, False, False, True, False, False]
    assert result == expected


def test_schedule_repr():
    s = Schedule(1, 1)
    s.set(0, 0, [1, 2])

    assert s.__repr__() == (
        "   0   \n"
        "   s  e\n"
        "0  1  2"
    )
