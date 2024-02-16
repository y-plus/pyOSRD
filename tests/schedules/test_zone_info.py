import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from pyosrd.schedules import step_has_fixed_duration, step_type, step_station_id
from pyosrd.schedules import schedule_from_osrd


def test_step_has_fixed_duration(use_case_station_capacity2):
    df = step_has_fixed_duration(use_case_station_capacity2)

    expected = pd.DataFrame(
        {
            0: [False, True, False, np.nan, True, True],
            1: [False, True, np.nan, False, True, True],
        },
        index=schedule_from_osrd(use_case_station_capacity2).df.index
    )

    assert_frame_equal(df, expected)


def test_step_type(use_case_station_capacity2):
    df = step_type(use_case_station_capacity2)

    expected = pd.DataFrame(
        {
            0: ['signal', 'switch', 'station', np.nan, 'switch', 'last_zone'],
            1: ['signal', 'switch', np.nan, 'station', 'switch', 'last_zone'],
        },
        index=schedule_from_osrd(use_case_station_capacity2).df.index
    )

    assert_frame_equal(df, expected)


def test_step_station_id(use_case_station_capacity2):
    df = step_station_id(use_case_station_capacity2)

    expected = pd.DataFrame(
        {
            0: [np.nan, np.nan, 'station', np.nan, np.nan, np.nan],
            1: [np.nan, np.nan, np.nan, 'station', np.nan, np.nan],
        },
        index=schedule_from_osrd(use_case_station_capacity2).df.index
    )

    assert_frame_equal(df, expected)
