import numpy as np
import pandas as pd
import PIL

from pandas.testing import assert_frame_equal


def test_schedules_delays(two_trains):
    delayed_schedule = (
        two_trains
        .shift_train_departure(train=0, time=3)
        .add_delay(train=1, block=1, delay=.5)
    )
    expected_delays = pd.DataFrame(
        {
            0: [3, np.nan, 3, 3, 3, np.nan],
            1: [np.nan, 0, .5, .5, np.nan, .5],
        }
    )
    assert_frame_equal(
        delayed_schedule.delays(two_trains),
        expected_delays
    )


def test_schedules_delays_zero(two_trains):
    expected_delays = pd.DataFrame(
        {
            0: [0, np.nan, 0, 0, 0, np.nan],
            1: [np.nan, 0, 0, 0, np.nan, 0],
        }
    )
    assert_frame_equal(
        two_trains.delays(two_trains),
        expected_delays
    )


def test_schedules_total_delays_at_stations(two_trains):
    delayed_schedule = (
        two_trains
        .shift_train_departure(train=0, time=3)
        .add_delay(train=1, block=1, delay=.5)
    )
    assert delayed_schedule.total_delay_at_stations(two_trains, [4, 5]) == 3.5


def test_schedules_compute_weighted_delays(two_trains):
    delayed_schedule = (
        two_trains
        .shift_train_departure(train=0, time=3)
        .add_delay(train=1, block=1, delay=.5)
    )
    weights = (
        delayed_schedule._df.loc[pd.IndexSlice[:], pd.IndexSlice[:, 's']]
        .set_axis(delayed_schedule._df.columns.levels[0], axis=1)
        .astype(float)
    ) * 0
    weights[weights.index.isin([4])] = 1
    assert delayed_schedule.compute_weighted_delays(two_trains, weights) == 3.0


def test_schedules_total_delays_at_station_zero(two_trains):
    assert two_trains.total_delay_at_stations(two_trains, [4, 5]) == 0


def test_schedules_train_delays(two_trains):
    delayed_schedule = (
        two_trains
        .shift_train_departure(train=0, time=3)
        .add_delay(train=1, block=1, delay=.5)
    )

    assert delayed_schedule.train_delay(0, two_trains) == 3.0
    assert delayed_schedule.train_delay(1, two_trains) == 0.5


def test_schedules_mermaid_graph(two_trains):
    assert two_trains._mermaid_graph == \
        'graph LR;2-->3;3-->4;3-->5;0-->2;1-->2'


def test_schedules_draw_graph_returns_image(two_trains):
    print(type(two_trains.draw_graph()))
    assert isinstance(
        two_trains.draw_graph(),
        PIL.JpegImagePlugin.JpegImageFile
    )
