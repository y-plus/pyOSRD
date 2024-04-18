"""Test schedule actions"""
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal


def test_schedules_conflicts(two_trains):
    delayed_schedule = two_trains.add_delay(
        train=0,
        zone=0,
        delay=0.5
    )

    assert_frame_equal(
        delayed_schedule.conflicts(train=0),
        pd.DataFrame(
            {'train2': [np.nan, np.nan, 2, 3, np.nan, np.nan]},
        )
    )
    assert_frame_equal(
        delayed_schedule.conflicts(train=1),
        pd.DataFrame(
            {'train1': [np.nan, np.nan, 1.5, 2.5, np.nan, np.nan]},
        )
    )


def test_schedules_no_conflict(two_trains):
    assert_frame_equal(
        two_trains.conflicts(train=0),
        pd.DataFrame({'train2': [np.nan] * 6},)
    )
    assert_frame_equal(
        two_trains.conflicts(train=1),
        pd.DataFrame({'train1': [np.nan] * 6},)
    )


def test_schedules_has_conflicts(two_trains):
    assert not two_trains.has_conflicts(train=0)
    assert not two_trains.has_conflicts(train=1)
    assert two_trains.add_delay(0, 0, .5).has_conflicts(train=0)
    assert two_trains.add_delay(0, 0, .5).has_conflicts(train=1)


def test_schedules_first_conflict(two_trains):
    delayed_schedule = two_trains.add_delay(
        train=0,
        zone=0,
        delay=0.5
    )
    assert delayed_schedule.first_conflict(train=0) == (2, 'train2')
    assert delayed_schedule.first_conflict(train=1) == (2, 'train1')


def test_schedules_earliest_conflict(two_trains):
    delayed_schedule = two_trains.add_delay(
        train=0,
        zone=0,
        delay=0.5
    )
    assert delayed_schedule.earliest_conflict() == (2, 'train1', 'train2')


def test_schedules_earliest_conflict_no_conflict(two_trains):
    assert two_trains.earliest_conflict() == (None, None, None)


def test_schedules_no_action_needed_no_conflict(three_trains):
    for train in range(2):
        assert not three_trains.is_action_needed(train=train)


def test_schedules_is_action_needed(three_trains):
    """Action is needed if, for a given train, there is a conflict
        the 1st conflict occurs at a point switch or just after
    """
    assert three_trains.add_delay(0, 0, .5).is_action_needed(train=0)
    assert three_trains.add_delay(0, 2, .5).is_action_needed(train=0)
    assert three_trains.add_delay(0, 3, .5).is_action_needed(train=0)
    assert not three_trains.add_delay(0, 4, .5).is_action_needed(train=0)

    assert three_trains.add_delay(0, 2, .5).is_action_needed(train=1)
    assert not three_trains.add_delay(0, 2, .5).is_action_needed(train=2)


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
