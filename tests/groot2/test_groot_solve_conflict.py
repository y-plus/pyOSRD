import pytest

from pyosrd.groot2 import Groot
from pyosrd.groot2.solve_conflict import solve_conflict


class TestsGrootSolveConflictsVUAFollowinge:
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_interlocking(
        self,
        groot2_vu_following: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_vu_following.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_vu_following,
            switch_order=False,
            leave_station_asap=True
        )
        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train00', 'train01')

    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_switch_order(
        self,
        groot2_vu_following: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_vu_following.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_vu_following,
            switch_order=True,
            leave_station_asap=True
        )
        assert dispatched_groot2 is None
        
        

class TestsGrootSolveConflictsVUAQlternate:
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_interlocking_leave_station_asap(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_vu_alternate.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_vu_alternate,
            switch_order=False,
            leave_station_asap=True
        )
        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train00', 'train01')
        
        assert dispatched_groot2.times['train00']['D.track.000.start->D.track.000.1'][1] == \
            pytest.approx(
                dispatched_groot2.times['train01']['D.track.000.start->D.track.000.1'][0]
            )
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_interlocking_leave_station_later(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_vu_alternate.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_vu_alternate,
            switch_order=False,
            leave_station_asap=False
        )
        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train00', 'train01')
        
        assert dispatched_groot2.times['train00']['D.track.000.start->D.track.000.1'][1] < \
                dispatched_groot2.times['train01']['D.track.000.start->D.track.000.1'][0]

    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_reorder_leave_station_asap(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_vu_alternate.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_vu_alternate,
            switch_order=True,
            leave_station_asap=True
        )
        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train01', 'train00')
        
        assert dispatched_groot2.times['train01']['D.track.000.start->D.track.000.1'][1] == \
            pytest.approx(
                dispatched_groot2.times['train00']['D.track.000.start->D.track.000.1'][0]
            )
    
    @pytest.mark.parametrize("delay", [270, 300, 320])
    def test_delay_A_reorder_leave_station_later(
        self,
        groot2_vu_alternate: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_vu_alternate.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_vu_alternate,
            switch_order=True,
            leave_station_asap=False
        )
        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'switch.001'
        ) == ('train01', 'train00')
        
        assert dispatched_groot2.times['train01']['D.track.000.start->D.track.000.1'][1] < \
                dispatched_groot2.times['train00']['D.track.000.start->D.track.000.1'][0]


class TestsGrootSolveConflictsInverseDirections:

    @pytest.mark.parametrize("delay", [300, 600])
    def test_delay_A_interlocking(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_crossing.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=False,
            leave_station_asap=False
        )

        assert dispatched_groot2.earliest_conflict('train00', 'train01')[0] is None

        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'A/V1'
        ) == ('train00', 'train01')
        
        assert dispatched_groot2 == solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=False,
            leave_station_asap=True
        )

    @pytest.mark.parametrize("delay", [300, 600])
    def test_delay_A_reorder(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_crossing.add_delay('train00', 'A/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=True,
            leave_station_asap=False
        )

        assert dispatched_groot2.earliest_conflict('train00', 'train01')[0] is None

        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train01',
            'A/V1'
        ) == ('train01', 'train00')
        
        assert dispatched_groot2 == solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=True,
            leave_station_asap=True
        )

    @pytest.mark.parametrize("delay", [300, 600, 900])
    def test_delay_B_interlocking(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_crossing.add_delay('train00', 'B/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=False,
            leave_station_asap=False
        )

        assert dispatched_groot2.earliest_conflict('train00', 'train03')[0] is None

        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        ) == groot2_crossing.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        )
        
        assert dispatched_groot2 == solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=False,
            leave_station_asap=True
        )

    @pytest.mark.parametrize("delay", [300, 600, 900])
    def test_delay_B_reorder(
        self,
        groot2_crossing: Groot, 
        delay: float
    ) -> None:
        disrupted_groot2 = groot2_crossing.add_delay('train00', 'B/V1', delay)
        dispatched_groot2 = solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=True,
            leave_station_asap=False
        )

        assert dispatched_groot2.earliest_conflict('train00', 'train03')[0] is None

        assert dispatched_groot2.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        ) == groot2_crossing.trains_order_in_zone(
            'train00',
            'train03',
            'C/V1'
        )[::-1]
        
        assert dispatched_groot2 == solve_conflict(
            disrupted_groot2,
            ref=groot2_crossing,
            switch_order=True,
            leave_station_asap=True
        )
