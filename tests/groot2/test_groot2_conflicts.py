import copy

from pyosrd.groot2.exploitation.modifications import add_delay


def test_groot2_has_conflicts(groot2_2trains) -> None:
    groot = copy.deepcopy(groot2_2trains)
    assert not groot.has_conflicts()
    add_delay(groot, 'train1', 'A', 2)
    assert groot.has_conflicts()


def test_groot2_earliest_conflict(groot2_2trains) -> None:
    groot = copy.deepcopy(groot2_2trains)
    add_delay(groot, 'train1', 'A', 2)
    assert groot.earliest_conflict() == ('train1', 'train2', 'A', 2)


def test_groot2_earliest_conflict2(groot2_2trains) -> None:
    groot = copy.deepcopy(groot2_2trains)
    add_delay(groot, 'train1', 'B', 2)
    assert groot.earliest_conflict() == ('train1', 'train2', 'B', 2.5)
