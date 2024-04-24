"""Test schedule actions"""
import numpy as np
import pandas as pd

from pandas.testing import assert_frame_equal

from pyosrd.schedules import Schedule


def test_schedules_shift_train_departure(two_trains):
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
    assert_frame_equal(result.df['train1'], expected)


def test_schedules_shift_train_departure_by_label(two_trains):
    result = two_trains.shift_train_departure(train='train1', time=2)
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
    assert_frame_equal(result.df['train1'], expected)


def test_schedules_set_priority_train(two_trains):
    result = two_trains.set_priority_train('train2', 'train1', 0, 2)
    expected_train1 = pd.DataFrame(
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

    assert_frame_equal(result.df['train1'], expected_train1)


def test_schedules_set_priority_train_2(two_trains):
    result = two_trains.set_priority_train('train2', 'train1', 0, 3)
    expected_train1 = pd.DataFrame(
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

    assert_frame_equal(result.df['train1'], expected_train1)


def test_schedules_set_priority_train_already_priority(two_trains):
    result = two_trains.set_priority_train('train1', 'train2', 1, 2)
    assert_frame_equal(result.df, two_trains.df)


def test_schedules_set_priority_train1_with_switch_delay(two_trains):

    expected = Schedule(6, 2)

    expected.df.at[0, 0] = [0, 1]
    expected.df.at[2, 0] = [1, 2]
    expected.df.at[3, 0] = [2, 3]
    expected.df.at[4, 0] = [3, 4]

    expected.df.at[1, 1] = [1, 2.5]
    expected.df.at[2, 1] = [2.5, 3.5]
    expected.df.at[3, 1] = [3.5, 4.5]
    expected.df.at[5, 1] = [4.5, 5.5]

    expected.set_train_labels(['train1', 'train2'])

    result = two_trains.set_priority_train(
        priority_train=0,
        train_decelerating=1,
        decelerates_in_zone=1,
        until_zone_is_free=2,
        switch_change_delay=0.5
    )
    assert_frame_equal(
        result.df,
        expected.df
    )


def test_schedules_set_priority_train2_with_switch_delay(two_trains):

    expected = Schedule(6, 2)

    expected.df.at[0, 0] = [0, 3.5]
    expected.df.at[2, 0] = [3.5, 4.5]
    expected.df.at[3, 0] = [4.5, 5.5]
    expected.df.at[4, 0] = [5.5, 6.5]

    expected.df.at[1, 1] = [1, 2]
    expected.df.at[2, 1] = [2, 3]
    expected.df.at[3, 1] = [3, 4]
    expected.df.at[5, 1] = [4, 5]

    expected.set_train_labels(['train1', 'train2'])

    result = two_trains.set_priority_train(
        priority_train=1,
        train_decelerating=0,
        decelerates_in_zone=0,
        until_zone_is_free=2,
        switch_change_delay=0.5
    )
    assert_frame_equal(
        result.df,
        expected.df
    )


def test_schedules_set_priority_1_block_btw_trains(two_trains_in_line):

    expected = Schedule(3, 2)

    expected.df.at[0, 0] = [0, 1]
    expected.df.at[1, 0] = [1, 2]
    expected.df.at[2, 0] = [2, 3]

    expected.df.at[0, 1] = [1, 3]
    expected.df.at[1, 1] = [3, 4]
    expected.df.at[2, 1] = [4, 5]

    expected.set_train_labels(['train1', 'train2'])

    result = two_trains_in_line.set_priority_train(
        priority_train=0,
        train_decelerating=1,
        decelerates_in_zone=0,
        until_zone_is_free=1,
        n_blocks_between_trains=1
    )
    assert_frame_equal(
        result.df,
        expected.df
    )
