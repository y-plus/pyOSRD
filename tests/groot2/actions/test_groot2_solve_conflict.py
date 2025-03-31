import copy
import pytest

from pyosrd.groot2 import Groot
from pyosrd.groot2.actions.solve_conflict import solve_conflict


class TestGrootSolveConflict:
   
    def test_returns_original_times(self, groot2_vu_following) -> None:
        groot = copy.deepcopy(groot2_vu_following)
        groot.add_delay('train00', 'A/V1', 300)
        expected_times = {
            'train01': copy.deepcopy(groot2_vu_following.times['train01'])
        }
        original_times = solve_conflict(
            groot,
            ref=groot2_vu_following,
            reorder=False,
            leave_station_asap=True
        )
        assert original_times == expected_times


class TestsGrootSolveConflictsVUFollowing:
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_interlocking(
        self,
        groot2_vu_following: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_vu_following)
        groot.add_delay('train00', 'A/V1', delay)
        solve_conflict(
            groot,
            ref=groot2_vu_following,
            reorder=False,
            leave_station_asap=True
        )
        assert groot.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train00', 'train01')

    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_reorder(
        self,
        groot2_vu_following: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_vu_following)
        groot.add_delay('train00', 'A/V1', delay)
        original_times = solve_conflict(
            groot,
            ref=groot2_vu_following,
            reorder=True,
            leave_station_asap=True
        )
        assert original_times is None
        
        

class TestsGrootSolveConflictsVUAlternate:
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_interlocking_leave_station_asap(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_vu_alternate)
        groot.add_delay('train00', 'A/V1', delay)
        solve_conflict(
            groot,
            ref=groot2_vu_alternate,
            reorder=False,
            leave_station_asap=True
        )
        assert groot.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train00', 'train01')
        
        assert groot.times['train00']['D.track.000.start->D.track.000.1'][1] == \
            pytest.approx(
                groot.times['train01']['D.track.000.start->D.track.000.1'][0]
            )
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_interlocking_leave_station_later(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_vu_alternate)
        groot.add_delay('train00', 'A/V1', delay)
        _ = solve_conflict(
            groot,
            ref=groot2_vu_alternate,
            reorder=False,
            leave_station_asap=False
        )
        assert groot.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train00', 'train01')
        
        assert groot.times['train00']['D.track.000.start->D.track.000.1'][1] < \
                groot.times['train01']['D.track.000.start->D.track.000.1'][0]

    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_reorder_leave_station_asap(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_vu_alternate)
        groot.add_delay('train00', 'A/V1', delay)
        solve_conflict(
            groot,
            ref=groot2_vu_alternate,
            reorder=True,
            leave_station_asap=True
        )
        assert groot.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train01', 'train00')
        
        assert groot.times['train01']['D.track.000.start->D.track.000.1'][1] == \
            pytest.approx(
                groot.times['train00']['D.track.000.start->D.track.000.1'][0]
            )
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_reorder_leave_station_later(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_vu_alternate)
        groot.add_delay('train00', 'A/V1', delay)
        _ = solve_conflict(
            groot,
            ref=groot2_vu_alternate,
            reorder=True,
            leave_station_asap=False
        )
        assert groot.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train01', 'train00')
        
        assert groot.times['train01']['D.track.000.start->D.track.000.1'][1] < \
                groot.times['train00']['D.track.000.start->D.track.000.1'][0]


class TestsGrootSolveConflictsInverseDirections:

    @pytest.mark.parametrize("delay", [300, 600])
    def test_delay_A_interlocking(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_crossing)
        groot.add_delay('train00', 'A/V1', delay)
        _ = solve_conflict(
            groot,
            ref=groot2_crossing,
            reorder=False,
            leave_station_asap=False
        )

        assert groot.earliest_conflict('train00', 'train01')[0] is None

        assert groot.trains_order_in_zone(
            'train00',
            'train01',
            'A/V1'
        ) == ('train00', 'train01')


    @pytest.mark.parametrize("delay", [300, 600])
    def test_delay_A_reorder(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_crossing)
        groot.add_delay('train00', 'A/V1', delay)
        assert solve_conflict(
            groot,
            ref=groot2_crossing,
            reorder=True,
            leave_station_asap=False
        ) is None


    @pytest.mark.parametrize("delay", [300, 600, 900])
    def test_delay_B_interlocking(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_crossing)
        groot.add_delay('train00', 'B/V1', delay)
        _ = solve_conflict(
            groot,
            ref=groot2_crossing,
            reorder=False,
            leave_station_asap=False
        )

        assert groot.earliest_conflict('train00', 'train03')[0] is None

        assert groot.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        ) == groot2_crossing.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        )


    @pytest.mark.parametrize("delay", [300, 600, 900])
    def test_delay_B_reorder(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        groot = copy.deepcopy(groot2_crossing)
        groot.add_delay('train00', 'B/V1', delay)
        _ = solve_conflict(
            groot,
            ref=groot2_crossing,
            reorder=True,
            leave_station_asap=False
        )

        assert groot.earliest_conflict('train00', 'train03')[0] is None

        assert groot.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        ) == groot2_crossing.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        )[::-1]
