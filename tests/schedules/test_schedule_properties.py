"""Test schedule properties"""
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from pyosrd.schedules import Schedule


def test_schedules_num_zones(three_trains):
    assert three_trains.num_zones == 6


def test_schedules_zones(three_trains):
    assert three_trains.zones == [0, 1, 2, 3, 4, 5]


def test_schedules_num_trains(three_trains):
    assert three_trains.num_trains == 3


def test_schedules_trains(three_trains):
    assert three_trains.trains == [0, 1, 2]


def test_schedules_df(three_trains):
    assert_frame_equal(three_trains._df, three_trains.df)


def test_schedule_set():
    s = Schedule(2, 2)
    s.set(0, 0, [0., 1.])
    assert s._df.loc[0, 0].values.tolist() == [0., 1.]


def test_schedules_starts(three_trains):
    expected = pd.DataFrame(
        {
            0: [0, np.nan, 1, 2, 3, np.nan],
            1: [np.nan, 1, 2, 3, np.nan, 4],
            2: [2, np.nan, 3, 4, 5, np.nan],
        },
    )
    assert_frame_equal(three_trains.starts, expected)


def test_schedules_ends(three_trains):
    expected = pd.DataFrame(
        {
            0: [1, np.nan, 2, 3, 4, np.nan],
            1: [np.nan, 2, 3, 4, np.nan, 5],
            2: [3, np.nan, 4, 5, 6, np.nan],
        },
    )
    assert_frame_equal(three_trains.ends, expected)


def test_schedules_durations(three_trains):
    expected = pd.DataFrame(
        {
            0: [1, np.nan, 1, 1, 1, np.nan],
            1: [np.nan, 1, 1, 1, np.nan, 1],
            2: [1, np.nan, 1, 1, 1, np.nan],
        },
    )
    assert_frame_equal(three_trains.durations, expected)
