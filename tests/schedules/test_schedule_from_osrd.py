import numpy as np
import pandas as pd

from pandas.testing import assert_frame_equal


def test_schedule_from_osrd(schedule_cvg_dvg):
    assert set(schedule_cvg_dvg.zones) == set([
        'D0<->buffer_stop.0',
        'CVG',
        'D2<->D3',
        'D1<->buffer_stop.1',
        'DVG',
        'D4<->buffer_stop.2',
        'D5<->buffer_stop.3',
    ])
    assert list(schedule_cvg_dvg._df.columns.levels[0]) == ['train0', 'train1']


def test_schedule_from_osrd_merge_switch_zones(schedule_double_switch):

    assert len(schedule_double_switch.zones) == 5
    assert 'SW0+SW1' in schedule_double_switch.zones


def test_schedule_from_osrd_trains(
    simulation_cvg_dvg,
    schedule_cvg_dvg
):
    assert schedule_cvg_dvg._trains == simulation_cvg_dvg.trains
    assert schedule_cvg_dvg.trains == simulation_cvg_dvg.trains


def test_schedule_from_osrd_step_type(schedule_station_capacity2):
    expected = pd.DataFrame(
        {
            'train0': [
                'signal', 'switch', 'station', np.nan, 'switch', 'last_zone'
            ],
            'train1': [
                'signal', 'switch', np.nan, 'station', 'switch', 'last_zone'
            ],
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
    assert_frame_equal(schedule_station_capacity2._step_type, expected)
    assert_frame_equal(schedule_station_capacity2.step_type, expected)


def test_schedule_from_osrd_min_times_base_only(schedule_station_capacity2):
    """No allowance, in this case times = min_times"""
    assert_frame_equal(
        schedule_station_capacity2.min_times,
        schedule_station_capacity2.df
    )


def test_schedule_from_osrd_min_times(
    schedule_straight_line
):
    """With allowance"""

    try:
        assert_frame_equal(
            schedule_straight_line.min_times,
            schedule_straight_line.df
        )
        raise AssertionError
    except AssertionError:
        pass
