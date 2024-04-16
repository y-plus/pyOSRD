import numpy as np

from pandas.testing import assert_frame_equal


def test_schedules_start_from_seconds(two_trains_hours):
    result = two_trains_hours.start_from(3_600)

    # first zone is different
    assert np.isnan(result.df.loc[1, ('train1', 's')])
    assert np.isnan(result.df.loc[1, ('train1', 'e')])

    # everything else remains equal
    assert_frame_equal(two_trains_hours.df.tail(5), result.df.tail(5))


def test_schedules_start_from_timestring(two_trains_hours):
    result = two_trains_hours.start_from('01:00')

    # first zone is different
    assert np.isnan(result.df.loc[1, ('train1', 's')])
    assert np.isnan(result.df.loc[1, ('train1', 'e')])

    # everything else remains equal
    assert_frame_equal(two_trains_hours.df.tail(5), result.df.tail(5))


def test_schedules_start_from_seconds_zones_skipped(two_trains_hours):
    """
    Expected result:
            train1            train2
            s        e        s        e
    1      NaN      NaN     5400   7200.0
    2     5400   7200.0   7200.0  10800.0
    3   7200.0  10800.0  10800.0  14400.0
    4  10800.0  14400.0      NaN      NaN
    5      NaN      NaN  14400.0  18000.0
    """
    result = two_trains_hours.start_from('01:30')

    # first zone does not appear anymore
    assert result.num_zones == 5

    # everything starts at 1h30
    assert result.df.min().min() == 3_600 * 1.5

    # everything after that remains equal
    assert_frame_equal(two_trains_hours.df.tail(3), result.df.tail(3))
