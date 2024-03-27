"""Test schedule actions"""
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal


def test_schedule_shift_train_departure(two_trains):
    result = two_trains.shift_train_departure(0, 2)
    expected = pd.DataFrame(
        [
            [2, 3],
            [np.nan, np.nan],
            [3, 4],
            [4, 5],
            [5, 6],
            [np.nan, np.nan],
        ],
        columns=['s', 'e'],
        dtype=object
    )
    assert_frame_equal(result.df[0], expected)


def test_schedule_shift_train_after_at_switch(two_trains):

    shifted = two_trains.shift_train_after(0, 1, 2)
    expected_train0 = pd.DataFrame(
        [
            [0, 3],
            [np.nan, np.nan],
            [3, 4],
            [4, 5],
            [5, 6],
            [np.nan, np.nan],
        ],
        columns=['s', 'e'],
        dtype=object
    )

    assert_frame_equal(shifted.df[0], expected_train0)
    assert_frame_equal(shifted.df[1], two_trains.df[1])


def test_schedule_shift_train_after_after_a_switch(two_trains):

    shifted = two_trains.shift_train_after(0, 1, 3)
    expected_train0 = pd.DataFrame(
        [
            [0, 3],
            [np.nan, np.nan],
            [3, 4],
            [4, 5],
            [5, 6],
            [np.nan, np.nan],
        ],
        columns=['s', 'e'],
        dtype=object
    )

    assert_frame_equal(shifted.df[0], expected_train0)
    assert_frame_equal(shifted.df[1], two_trains.df[1])


def test_schedule_shift_train_after_at_departure(three_trains):

    shifted = three_trains.shift_train_after(0, 2, 0)
    expected_train0 = pd.DataFrame(
        [
            [3, 4],
            [np.nan, np.nan],
            [4, 5],
            [5, 6],
            [6, 7],
            [np.nan, np.nan],
        ],
        columns=['s', 'e'],
        dtype=object
    )

    assert_frame_equal(shifted.df[0], expected_train0)
    assert_frame_equal(shifted.df[2], three_trains.df[2])


def test_schedules_propagate_delay_action_needed(
    two_trains_two_zones_before_dvg
):
    """conflict occurs at point switch => action/decision needed
        => notihng is propagated
    """
    propagated, _ = (
        two_trains_two_zones_before_dvg
        .add_delay(train=0, zone=2, delay=.5)
        .propagate_delay(delayed_train=0)
    )

    assert_frame_equal(
        two_trains_two_zones_before_dvg.add_delay(
            train=0,
            zone=2,
            delay=.5
        ).df,
        propagated.df
    )


def test_schedules_propagate_delay(
    two_trains_two_zones_before_dvg
):
    propagated, _ = (
        two_trains_two_zones_before_dvg
        .add_delay(train=0, zone=4, delay=.5)
        .propagate_delay(delayed_train=0)
    )

    expected = pd.DataFrame(
        {
            0: [1, np.nan, 2, 3, 4.5, 5.5, np.nan],
            1: [np.nan, 2, 3, 4.5, 5.5, np.nan, 6.5],
        }
    )

    assert_frame_equal(propagated.ends, expected)
