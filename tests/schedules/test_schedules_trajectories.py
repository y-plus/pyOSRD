
from pyosrd.schedules import Schedule


def test_schedules_trajectory_by_index(three_trains):
    assert three_trains.trajectory(0) == [0, 2, 3, 4]
    assert three_trains.trajectory(1) == [1, 2, 3, 5]
    assert three_trains.trajectory(2) == [0, 2, 3, 4]


def test_schedules_trajectory_by_label(three_trains):
    assert three_trains.trajectory('train1') == [0, 2, 3, 4]
    assert three_trains.trajectory('train2') == [1, 2, 3, 5]
    assert three_trains.trajectory('train3') == [0, 2, 3, 4]


def test_schedules_previous_zone_by_index(three_trains):
    assert three_trains.previous_zone(0, 0) is None
    assert three_trains.previous_zone(0, 2) == 0
    assert three_trains.previous_zone(0, 4) == 3


def test_schedules_previous_zone_by_label(three_trains):
    assert three_trains.previous_zone('train1', 0) is None
    assert three_trains.previous_zone('train1', 2) == 0
    assert three_trains.previous_zone('train1', 4) == 3


def test_schedules_next_zone_by_index(three_trains):
    assert three_trains.next_zone(0, 0) == 2
    assert three_trains.next_zone(0, 2) == 3
    assert three_trains.next_zone(0, 4) is None


def test_schedules_next_zone_by_label(three_trains):
    assert three_trains.next_zone('train1', 0) == 2
    assert three_trains.next_zone('train1', 2) == 3
    assert three_trains.next_zone('train1', 4) is None


def test_schedules_is_a_point_switch(two_trains):
    result = [
        two_trains.is_a_point_switch(0, 1, tr)
        for tr in two_trains.zones
    ]
    expected = [False, False, True, False, False, False]
    assert result == expected


def test_schedules_is_just_after_a_point_switch(two_trains):
    result = [
        two_trains.is_just_after_a_point_switch(0, 1, tr)
        for tr in two_trains.zones
    ]
    expected = [False, False, False, True, False, False]
    assert result == expected


def test_schedules_repr():
    s = Schedule(1, 1)
    s.set(0, 0, [1, 2])

    assert s.__repr__() == (
        "   0   \n"
        "   s  e\n"
        "0  1  2"
    )


def test_schedules_trains_order_in_zone(three_trains):
    assert three_trains.trains_order_in_zone('train3', 'train1', 2) == \
        ['train1', 'train3']
    assert three_trains.trains_order_in_zone(1, 0, 1) == ['train2']
