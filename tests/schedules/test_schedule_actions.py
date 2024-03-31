"""Test schedule actions"""
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal


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
