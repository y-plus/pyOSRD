import copy


def test_groot2_has_conflicts(groot2_2trains) -> None:
    groot = copy.deepcopy(groot2_2trains)
    assert not groot.has_conflicts()
    groot.add_delay('train1', 'A->B', 2)
    assert groot.has_conflicts()


def test_groot2_earliest_conflict(groot2_2trains) -> None:
    groot = copy.deepcopy(groot2_2trains)
    groot.add_delay('train1', 'A->B', 2)
    assert groot.earliest_conflict() == ('train1', 'train2', 'A->B', 0)


def test_groot2_earliest_conflict2(groot2_2trains) -> None:
    groot = copy.deepcopy(groot2_2trains)
    groot.add_delay('train1', 'B->C', 2)
    assert groot.earliest_conflict() == ('train1', 'train2', 'B->C', 2.5)
