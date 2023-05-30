"""Test schedule properties"""
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import networkx as nx
from networkx.utils import edges_equal, nodes_equal

from rlway.schedules import Schedule


def test_schedules_num_blocks(three_trains):
    assert three_trains.num_blocks == 6


def test_schedules_blocks(three_trains):
    assert three_trains.blocks == [0, 1, 2, 3, 4, 5]


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


def test_schedules_lengths(three_trains):
    expected = pd.DataFrame(
        {
            0: [1, np.nan, 1, 1, 1, np.nan],
            1: [np.nan, 1, 1, 1, np.nan, 1],
            2: [1, np.nan, 1, 1, 1, np.nan],
        },
    )
    assert_frame_equal(three_trains.lengths, expected)


def test_schedules_trajectory(three_trains):
    assert three_trains.trajectory(0) == [0, 2, 3, 4]
    assert three_trains.trajectory(1) == [1, 2, 3, 5]
    assert three_trains.trajectory(2) == [0, 2, 3, 4]


def test_previous_block(three_trains):
    assert three_trains.previous_block(0, 0) is None
    assert three_trains.previous_block(0, 2) == 0
    assert three_trains.previous_block(0, 4) == 3


def test_next_block(three_trains):
    assert three_trains.next_block(0, 0) == 2
    assert three_trains.next_block(0, 2) == 3
    assert three_trains.next_block(0, 4) is None


def test_is_a_point_switch(two_trains):
    result = [
        two_trains.is_a_point_switch(0, 1, tr)
        for tr in two_trains.blocks
    ]
    expected = [False, False, True, False, False, False]
    assert result == expected


def test_is_just_after_a_point_switch(two_trains):
    result = [
        two_trains.is_just_after_a_point_switch(0, 1, tr)
        for tr in two_trains.blocks
    ]
    expected = [False, False, False, True, False, False]
    assert result == expected


def test_schedule_graph(two_trains):

    G = nx.DiGraph([
        (0, 2),
        (1, 2),
        (2, 3),
        (3, 4),
        (3, 5)
    ])

    nx.set_node_attributes(
        G,
        {
            0: np.array([0, 1, 0, 0]),
            1: np.array([0, 0, 1, 2]),
            2: np.array([1, 2, 2, 3]),
            3: np.array([2, 3, 3, 4]),
            4: np.array([3, 4, 0, 0]),
            5: np.array([0, 0, 4, 5]),
        },
        'times'
    )

    assert nodes_equal(G.nodes, two_trains.graph.nodes)
    assert edges_equal(G.edges, two_trains.graph.edges)


def test_schedule_repr():
    s = Schedule(1, 1)
    s.set(0, 0, [1, 2])

    assert s.__repr__() == (
        "   0   \n"
        "   s  e\n"
        "0  1  2"
    )
