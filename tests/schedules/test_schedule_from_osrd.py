import numpy as np
import pandas as pd

from pandas.testing import assert_frame_equal

from pyosrd.schedules import schedule_from_osrd
from pyosrd.schedules.from_osrd import _schedule_df_from_OSRD


def test_schedule_from_osrd(use_case_cvg_dvg):
    s = schedule_from_osrd(use_case_cvg_dvg)
    assert set(s.zones) == set([
        'D0<->buffer_stop.0',
        'CVG',
        'D2<->D3',
        'D1<->buffer_stop.1',
        'DVG',
        'D4<->buffer_stop.2',
        'D5<->buffer_stop.3',
    ])
    assert list(s._df.columns.levels[0]) == ['train0', 'train1']


def test_schedule_from_osrd_merge_switch_zones(use_case_double_switch):
    s = schedule_from_osrd(use_case_double_switch)

    assert len(s.zones) == 5
    assert 'SW0+SW1' in s.zones


def test_schedule_from_osrd_trains(use_case_cvg_dvg):
    s = schedule_from_osrd(use_case_cvg_dvg)
    assert s._trains == use_case_cvg_dvg.trains
    assert s.trains == use_case_cvg_dvg.trains


def test_schedule_from_osrd_step_type(use_case_station_capacity2):
    s = schedule_from_osrd(use_case_station_capacity2)
    expected = pd.DataFrame(
        {
            0: ['signal', 'switch', 'station', np.nan, 'switch', 'last_zone'],
            1: ['signal', 'switch', np.nan, 'station', 'switch', 'last_zone'],
        },
        index=[
            'D0<->buffer_stop.0',
            'DVG',
            'D1<->D3',
            'D2<->D4',
            'CVG',
            'D5<->buffer_stop.5',
        ]
    )
    assert_frame_equal(s._step_type, expected)
    assert_frame_equal(s.step_type, expected)


def test_schedule_from_osrd_min_times_base_only(use_case_station_capacity2):
    """No allowance, in this case times = min_times"""
    s = schedule_from_osrd(use_case_station_capacity2)
    assert_frame_equal(s.min_times, s.df)


def test_schedule_from_osrd_min_times(use_case_straight_line):
    """No allowance, in this case times = min_times"""
    s = schedule_from_osrd(use_case_straight_line)
    assert_frame_equal(
        s.min_times,
        _schedule_df_from_OSRD(use_case_straight_line, eco_or_base='base')
    )
