import copy
import pytest

from pyosrd.groot2 import Groot
from pyosrd.groot2.actions.evaluate_action import evaluate_action


def test_evaluate_action_returns_original_times(groot2_vu_following) -> None:
    
    expected_times = {
        'train01': copy.deepcopy(groot2_vu_following.times['train01'])
    }

    groot = copy.deepcopy(groot2_vu_following)
    groot.add_delay('train00', 'A/V1', 300)
    original_times = evaluate_action(
        groot,
        ref=groot2_vu_following,
        action='S'
    )
    assert original_times == expected_times


def test_evaluate_action_unvalid_action(groot2_vu_following) -> None:

    groot = copy.deepcopy(groot2_vu_following)
    groot.add_delay('train00', 'A/V1', 300)
    original_times = evaluate_action(
        groot,
        ref=groot2_vu_following,
        action=''
    )
    assert original_times is None


def test_delay_A_action_S(groot2_vu_following: Groot) -> None:
    groot = copy.deepcopy(groot2_vu_following)
    groot.add_delay('train00', 'A/V1', 300)
    evaluate_action(
        groot,
        ref=groot2_vu_following,
        action='S'
    )
    assert groot.trains_order_in_zone(
        'train00',
        'train01',
        'switch.001'
    ) == ('train00', 'train01')


def test_delay_A_action_O(groot2_vu_alternate: Groot) -> None:
    groot = copy.deepcopy(groot2_vu_alternate)
    groot.add_delay('train00', 'A/V1', 300)
    evaluate_action(
        groot,
        ref=groot2_vu_alternate,
        action='O'
    )
    assert groot.trains_order_in_zone(
        'train00',
        'train01',
        'switch.001'
    ) == ('train01', 'train00')


def test_delay_A_action_R(groot2_vu_following: Groot) -> None:
    groot = copy.deepcopy(groot2_vu_following)
    groot.add_delay('train00', 'A/V1', 300)
    assert evaluate_action(
        groot,
        ref=groot2_vu_following,
        action='R'
    ) is None


def test_evaluate_action_R(groot2_reroute: Groot) -> None:

    groot = copy.deepcopy(groot2_reroute)
    groot.add_delay('train0', 'station/T2', 120)
    # station/T4 is free (see picture)
    evaluate_action(
        groot,
        groot2_reroute,
        'R'
    )
    assert 'station/T4' in groot.times_zones['train2']
    
    # All lanes are now occupied
    assert evaluate_action(
        groot,
        groot2_reroute,
        'R'
    ) is None