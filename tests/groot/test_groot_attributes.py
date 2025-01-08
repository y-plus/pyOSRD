
import pandas as pd

from pandas.testing import assert_frame_equal


def test_groot_trains(groot_1train, groot_2trains):
    assert groot_1train.trains == ['train1']
    assert groot_2trains.trains == ['train1', 'train2']


def test_groot_path(groot_1train):
    assert groot_1train.path('train1') == ['A', 'B', 'C']


def test_groot_train_zones(groot_1train):
    assert groot_1train.train_zones('train1') == ['A', 'B', 'C']


def test_groot_times_zones(groot_1train):
    assert groot_1train.times_zones == {
        'train1': {
            'A': (0, 3),
            'B': (2.5, 5.5),
            'C': (5, 8),
        },
    }

def test_groot_zones_graph(groot_1train):
    graph = groot_1train.zones_graph
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert list(graph.nodes) == ['A', 'B', 'C']


def test_groot_to_df(groot_2trains):
    df = groot_2trains.to_df()
    expected = pd.DataFrame(
        columns=pd.MultiIndex.from_product(
            [['train1', 'train2'], ['s', 'e']]
        ),
        index=['A', 'B', 'C'],
        data=[
            [0, 3, 4, 7],
            [2.5, 5.5, 6.5, 9.5],
            [5, 8, 9, 12],
        ]
    )
    assert_frame_equal(df, expected)


def test_groot_add_delay_start(groot_1train):
    delayed = groot_1train.add_delay('train1', 'A', 1)
    expected_times = {
        'A': (1, 4),
        'B': (3.5, 6.5),
        'C': (6, 9),
    }
    assert delayed.times['train1'] == expected_times

def test_groot_add_delay(groot_1train):
    delayed = groot_1train.add_delay('train1', 'B', 1)
    expected_times = {
        'A': (0, 3),
        'B': (2.5, 6.5),
        'C': (6, 9),
    }
    assert delayed.times['train1'] == expected_times


def test_groot_departure_times(groot_2trains):
    assert groot_2trains.departure_times == {'train1': 0, 'train2': 4}


def test_groot_last_arrival_times(groot_2trains):
    assert groot_2trains.last_arrival_times == {'train1': 8, 'train2': 12}


def test_groot_trains_in_zone(groot_2trains):
    assert groot_2trains.trains_in_zone('A') == ['train1', 'train2']


def test_groot_next_train(groot_2trains):
    assert groot_2trains.next_train('train1', 'A') == 'train2'
    assert groot_2trains.next_train('train2', 'A') is None


def test_groot_previous_train(groot_2trains):
    assert groot_2trains.previous_train('train1', 'A') is None
    assert groot_2trains.previous_train('train2', 'A') == 'train1'


def test_groot_trains_order_in_zone(groot_2trains):
        assert groot_2trains.trains_order_in_zone('train2', 'train1', 'B') ==\
            ('train1', 'train2')


def test_groot_previous_zones(groot_1train):
    assert groot_1train.previous_zones('train1', 'A') == []
    assert groot_1train.previous_zones('train1', 'B') == ['A']
    assert groot_1train.previous_zones('train1', 'C') == ['B', 'A']


def test_groot_next_zones(groot_1train):
    assert groot_1train.next_zones('train1', 'A') == ['B', 'C']
    assert groot_1train.next_zones('train1', 'B') == ['C']
    assert groot_1train.next_zones('train1', 'C') == []


def test_groot_previous_station(groot_1train):
    assert groot_1train.previous_station('train1', 'A') is None
    assert groot_1train.previous_station('train1', 'B') == 'A'
    assert groot_1train.previous_station('train1', 'C') == 'A'


def test_groot_next_station(groot_1train):
    assert groot_1train.next_station('train1', 'A') == 'C'
    assert groot_1train.next_station('train1', 'B') == 'C'
    assert groot_1train.next_station('train1', 'C') is None
