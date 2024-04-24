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


def test_schedules_conflict_when_there_s_no(two_trains):
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


def test_schedules_train_first_conflict(two_trains):
    delayed_schedule = two_trains.add_delay(
        train=0,
        zone=0,
        delay=0.5
    )
    assert delayed_schedule.train_first_conflict(train=0) == (2, 'train2')
    assert delayed_schedule.train_first_conflict(train=1) == (2, 'train1')


def test_schedules_earliest_conflict(two_trains):
    delayed_schedule = two_trains.add_delay(
        train=0,
        zone=0,
        delay=0.5
    )
    assert delayed_schedule.earliest_conflict() == (2, 'train1', 'train2')


def test_schedules_earliest_conflict_no_conflict(two_trains):
    assert two_trains.earliest_conflict() == (None, None, None)


def test_schedules_first_conflict_zone(two_trains):
    assert two_trains.first_conflict_zone(0, 1) is None


def test_schedules_first_conflict_zone_non(two_trains):
    assert (
        two_trains
        .add_delay(0, 0, 0.5)
        .first_conflict_zone(0, 1)
     ) == 2


def test_schedules_are_conflicted(two_trains):
    assert two_trains.add_delay(0, 0, 0.5).are_conflicted(0, 1)


def test_schedules_are_conflicted_false(two_trains):
    assert not two_trains.are_conflicted(0, 1)


def test_schedules_no_conflict_false(two_trains):
    assert not two_trains.add_delay(0, 0, 0.5).no_conflict()


def test_schedules_no_conflict(two_trains):
    assert two_trains.no_conflict()
