
from pyosrd.schedules import Schedule


def test_schedules_path_by_index(three_trains):
    assert three_trains.path(0) == [0, 2, 3, 4]
    assert three_trains.path(1) == [1, 2, 3, 5]
    assert three_trains.path(2) == [0, 2, 3, 4]


def test_schedules_path_by_label(three_trains):
    assert three_trains.path('train1') == [0, 2, 3, 4]
    assert three_trains.path('train2') == [1, 2, 3, 5]
    assert three_trains.path('train3') == [0, 2, 3, 4]


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


def test_schedules_first_in(two_trains):
    for zone in (0, 2, 3, 4):
        assert (
            two_trains.add_delay(0, 0, 0.5)
            .first_in(0, 1, zone)
            == 'train1'
        )
    for zone in (1, 2, 3, 5):
        assert (
            two_trains.add_delay(0, 0, 1.5)
            .first_in(0, 1, zone)
            == 'train2'
        )


def test_schedules_first_in_same_time(two_trains):
    assert (
        two_trains.add_delay(0, 0, 1)
        .first_in(0, 1, 2)
        == ['train1', 'train2']
    )
