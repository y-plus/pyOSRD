from pyosrd.groot2 import Groot

def test_groot2_trains(groot2_1train, groot2_2trains: Groot) -> None:
    assert groot2_1train.trains == ['train1']
    assert groot2_2trains.trains == ['train1', 'train2']


def test_groot2_path(groot2_1train: Groot) -> None:
    assert groot2_1train.path('train1') == ['A->B', 'B->C', 'C->D']


def test_groot2_train_zones(groot2_1train: Groot) -> None:
    assert groot2_1train.path_zones('train1') == ['A->B', 'B->C', 'C->D']


def test_groot2_times_zones(groot2_1train: Groot) -> None:
    assert groot2_1train.times_zones == {
        'train1': {
            'A->B': (0, 3),
            'B->C': (2.5, 5.5),
            'C->D': (5, 8),
        },
    }


def test_groot2_zones_graph(groot2_1train: Groot) -> None:
    graph = groot2_1train.zones_graph
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert list(graph.nodes) == ['A->B', 'B->C', 'C->D']


def test_groot2_departure_times(groot2_2trains: Groot) -> None:
    assert groot2_2trains.departure_times == {'train1': 0, 'train2': 4}


def test_groot2_last_arrival_times(groot2_2trains: Groot) -> None:
    assert groot2_2trains.last_arrival_times == {'train1': 8, 'train2': 12}


def test_groot2_trains_in_zone(groot2_2trains: Groot) -> None:
    assert groot2_2trains.trains_in_zone('A->B') == ['train1', 'train2']


def test_groot2_next_train(groot2_2trains: Groot) -> None:
    assert groot2_2trains.next_train('train1', 'A->B') == 'train2'
    assert groot2_2trains.next_train('train2', 'A->B') is None


def test_groot2_previous_train(groot2_2trains: Groot) -> None:
    assert groot2_2trains.previous_train('train1', 'A->B') is None
    assert groot2_2trains.previous_train('train2', 'A->B') == 'train1'


def test_groot2_trains_order_in_zone(groot2_2trains: Groot) -> None:
    assert groot2_2trains.trains_order_in_zone('train2', 'train1', 'B->C') ==\
        ('train1', 'train2')


def test_groot2_previous_zones(groot2_1train: Groot) -> None:
    assert groot2_1train.previous_zones('train1', 'A->B') == []
    assert groot2_1train.previous_zones('train1', 'B->C') == ['A->B']
    assert groot2_1train.previous_zones('train1', 'C->D') == ['B->C', 'A->B']


def test_groot2_next_zones(groot2_1train: Groot) -> None:
    assert groot2_1train.next_zones('train1', 'A->B') == ['B->C', 'C->D']
    assert groot2_1train.next_zones('train1', 'B->C') == ['C->D']
    assert groot2_1train.next_zones('train1', 'C->D') == []


def test_groot2_previous_station(groot2_1train: Groot) -> None:
    assert groot2_1train.previous_station('train1', 'A->B') is None
    assert groot2_1train.previous_station('train1', 'B->C') == 'A->B'
    assert groot2_1train.previous_station('train1', 'C->D') == 'A->B'


def test_groot2_next_station(groot2_1train: Groot) -> None:
    assert groot2_1train.next_station('train1', 'A->B') == 'C->D'
    assert groot2_1train.next_station('train1', 'B->C') == 'C->D'
    assert groot2_1train.next_station('train1', 'C->D') is None
