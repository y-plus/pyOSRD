import copy

from pyosrd.groot2 import Groot
from pyosrd.groot2.rerouting import reroute_train_to_avoid_zone


def test_rerouting( groot2_reroute: Groot) -> None:

    groot = copy.deepcopy(groot2_reroute)

    # station/T4 is free (see picture)
    reroute_train_to_avoid_zone(
        groot,
        'train2',
        'station/T2'

    )
    assert 'station/T4' in groot.times_zones['train2']
    
    # All lanes are now occupied
    assert reroute_train_to_avoid_zone(
        groot,
        'train1',
        'station/T3'
    ) is None


def test_rerouting_returns_original_times(groot2_reroute) -> None:
    groot = copy.deepcopy(groot2_reroute)
    original_times = {'train2': groot2_reroute.times['train2']}
    modified_times = reroute_train_to_avoid_zone(
        groot,
        'train2',
        'station/T2'

    )
    assert modified_times == original_times