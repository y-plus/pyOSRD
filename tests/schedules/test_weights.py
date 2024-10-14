import pandas as pd
from pandas.testing import assert_frame_equal

import pyosrd.schedules.weights as weights


def test_weights_all_steps(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    w = weights.all_steps(simulation_station_capacity2)

    expected = pd.DataFrame(
        {
            'train0': [1, 1, 1, 0, 1, 1],
            'train1': [1, 1, 0, 1, 1, 1],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(w, expected)


def test_weights_stations_only(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    w = weights.stations_only(simulation_station_capacity2)

    expected = pd.DataFrame(
        {
            'train0': [0, 0, 1, 0, 0, 0],
            'train1': [0, 0, 0, 1, 0, 0],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(w, expected)


def test_weights_set_for_one_train(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    w = weights.all_steps(simulation_station_capacity2)
    w.weights.train(0, 2)
    expected = pd.DataFrame(
        {
            'train0': [2, 2, 2, 0, 2, 2],
            'train1': [1, 1, 0, 1, 1, 1],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(w, expected)


def test_weights_set_for_one_step(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    w = weights.all_steps(simulation_station_capacity2)
    w.weights.train_zone(0, 'DVG', 2)
    expected = pd.DataFrame(
        {
            'train0': [1, 2, 1, 0, 1, 1],
            'train1': [1, 1, 0, 1, 1, 1],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(w, expected)


def test_weights_set_for_one_train_at_a_station(
    simulation_station_capacity2,
    schedule_station_capacity2
):
    w = weights.all_steps(simulation_station_capacity2)
    w.weights.train_station_sim(0, 'station/V3', 2, simulation_station_capacity2)
    w.weights.train_station_sim(1, 'station/V4', 2, simulation_station_capacity2)
    expected = pd.DataFrame(
        {
            'train0': [1, 1, 2, 0, 1, 1],
            'train1': [1, 1, 0, 2, 1, 1],
        },
        index=schedule_station_capacity2.df.index
    )

    assert_frame_equal(w, expected)
