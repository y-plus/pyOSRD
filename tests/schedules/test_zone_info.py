import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from pyosrd.schedules import (
    step_has_fixed_duration,
    step_type,
    step_station_id,
)


def test_step_has_fixed_duration(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    df = step_has_fixed_duration(simulation_station_capacity2)

    expected = pd.DataFrame(
        {
            'train0': [False, True, False, np.nan, True, True],
            'train1': [False, True, np.nan, False, True, True],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(df, expected)


def test_step_type(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    df = step_type(simulation_station_capacity2)

    expected = pd.DataFrame(
        {
            'train0': ['signal', 'switch', 'station', np.nan, 'switch', 'last_zone'],  # noqa
            'train1': ['signal', 'switch', np.nan, 'station', 'switch', 'last_zone'],  # noqa
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(df, expected)


def test_step_station_id(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    df = step_station_id(simulation_station_capacity2)

    expected = pd.DataFrame(
        {
            'train0': [np.nan, np.nan, 'station', np.nan, np.nan, np.nan],
            'train1': [np.nan, np.nan, np.nan, 'station', np.nan, np.nan],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(df, expected)
