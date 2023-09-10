"""
point_switch
----------

                     S1┐
                    -D1---------(T1)-->
            ┎S0   / 
--(T0)--------D0-<(DVG)            
                  \  S2┐ 
                    -D2----------(T2)-->

All tracks are 10 km long
Train 0 starts from the beginning of T0 at t=0s, and arrives at the end of T1
Train 1 starts from the end of T2 at t=60s, and arrives at the beginning of T0
"""  # noqa

from dataclasses import asdict

import matplotlib.pyplot as plt

from rlway.pyosrd.osrd import Point


def test_point_switch_infra(use_case_point_switch):
    assert isinstance(use_case_point_switch.infra, dict)


def test_point_switch_infra_routes(use_case_point_switch):
    assert set(use_case_point_switch.routes) == \
        set([
            'rt.buffer_stop.0->D0',
            'rt.D0->buffer_stop.2',
            'rt.D0->buffer_stop.1',
            'rt.buffer_stop.1->D1',
            'rt.D1->buffer_stop.0',
            'rt.buffer_stop.2->D2',
            'rt.D2->buffer_stop.0',
        ])


def test_point_switch_infra_track_lengths(use_case_point_switch):
    assert use_case_point_switch.track_section_lengths == \
        {
            'T0': 10_000.0,
            'T1': 10_000.0,
            'T2': 10_000.0,
        }


def test_point_switch_infra_num_switches(use_case_point_switch):
    assert use_case_point_switch.num_switches == 1


def test_point_switch_infra_draw_infra_not_fail(use_case_point_switch):
    """Test if it does not raise an exception"""
    try:
        use_case_point_switch.draw_infra()
    except:  # noqa
        assert False


def test_point_switch_infra_station_capacities(use_case_point_switch):
    assert (
        use_case_point_switch.station_capacities == {}
    )


def test_point_switch_infra_num_stations(use_case_point_switch):
    assert use_case_point_switch.num_stations == 0


def test_point_switch_points_on_tracks(use_case_point_switch):
    expected = {
        'T0': [
            Point(id='buffer_stop.0', track_section='T0', position=0.0, type='buffer_stop'),  # noqa
            Point(track_section='T0', id='S0', position=9800.0, type='signal'),  # noqa
            Point(track_section='T0', id='D0', position=9820.0, type='detector'),  # noqa
            Point(track_section='T0', id='DVG', position=10000.0, type='switch'),  # noqa
        ],
        'T1': [
            Point(track_section='T1', id='DVG', position=0, type='switch'),  # noqa
            Point(track_section='T1', id='D1', position=180.0, type='detector'),  # noqa
            Point(track_section='T1', id='S1', position=200.0, type='signal'),  # noqa
             Point(id='buffer_stop.1', track_section='T1', position=10000.0, type='buffer_stop'),  # noqa
        ],
        'T2': [
            Point(track_section='T2', id='DVG', position=0, type='switch'),  # noqa
            Point(track_section='T2', id='D2', position=180.0, type='detector'),  # noqa
            Point(track_section='T2', id='S2', position=200.0, type='signal'),  # noqa
            Point(id='buffer_stop.2', track_section='T2', position=10000.0, type='buffer_stop'),  # noqa
        ],
    }

    assert use_case_point_switch.points_on_track_sections() == expected


def test_point_switch_simulation_type(use_case_point_switch):
    assert isinstance(use_case_point_switch.simulation, dict)


def test_point_switch_simulation_num_trains(use_case_point_switch):
    assert use_case_point_switch.num_trains == 2


def test_point_switch_simulation_trains(use_case_point_switch):
    assert use_case_point_switch.trains == ['train0', 'train1']


def test_point_switch_simulation_departure_times(use_case_point_switch):
    assert use_case_point_switch.departure_times == [0, 100]


def test_point_switch_results_length(use_case_point_switch):
    assert len(use_case_point_switch.results) == \
        use_case_point_switch.num_trains


def test_point_switch_results_train_track_sections(use_case_point_switch):
    assert use_case_point_switch.train_track_sections(0) == [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'T1', 'direction': 'START_TO_STOP'},
    ]
    assert use_case_point_switch.train_track_sections(1) == [
        {'id': 'T2', 'direction': 'STOP_TO_START'},
        {'id': 'T0', 'direction': 'STOP_TO_START'},
    ]


def test_point_switch_departure_arrival_0(use_case_point_switch):
    assert asdict(use_case_point_switch.train_departure(0)) == {
        'id': 'departure_train0',
        'track_section': 'T0',
        'position': 50.0,
        'type': 'departure',
    }
    assert asdict(use_case_point_switch.train_arrival(0)) == {
        'id': 'arrival_train0',
        'track_section': 'T1',
        'position': 9950.0,
        'type': 'arrival',
    }


def test_point_switch_departure_arrival_1(use_case_point_switch):
    assert asdict(use_case_point_switch.train_departure(1)) == {
        'id': 'departure_train1',
        'track_section': 'T2',
        'position': 9950.0,
        'type': 'departure',
    }
    assert asdict(use_case_point_switch.train_arrival(1)) == {
        'id': 'arrival_train1',
        'track_section': 'T0',
        'position': 50.0,
        'type': 'arrival',
    }


def test_point_switch_offset_in_path(use_case_point_switch):
    before_departure_0 = Point(
        id='before_departure_0',
        track_section='T0',
        position=30.0,
        type='point'
    )
    after_arrival_0 = Point(
        id='after_arrival_0',
        track_section='T1',
        position=9980.0,
        type='point'
    )

    before_departure_1 = Point(
        id='before_departure_1',
        track_section='T2',
        position=9980.0,
        type='point'
    )
    after_arrival_1 = Point(
        id='after_arrival_1',
        track_section='T0',
        position=30.0,
        type='point'
    )

    assert [
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch.train_departure(0), train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch.train_departure(1), train=1),  # noqa
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch.train_arrival(0), train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch.train_arrival(1), train=1),  # noqa
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch.train_arrival(0), train=1),  # noqa
        use_case_point_switch.offset_in_path_of_train(before_departure_0, train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(after_arrival_0, train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(before_departure_1, train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(after_arrival_1, train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch._points()[-3], train=0),  # noqa
        use_case_point_switch.offset_in_path_of_train(use_case_point_switch._points()[-1], train=1),  # noqa

    ] == [0.0, 0.0, 19900.0, 19900.0, None, None, 19930, None, None, 9950.0, 9950.0]  # noqa


def test_point_switch_points_encountered_by_train0(use_case_point_switch):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in use_case_point_switch.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'departure_train0', 'type': 'departure', 'offset': 0, },
        {'id': 'S0', 'offset': 9750.0, 'type': 'signal'},
        {'id': 'D0', 'offset': 9770.0, 'type': 'detector'},
        {'id': 'DVG', 'offset': 9950.0, 'type': 'switch'},
        {'id': 'D1', 'offset': 10130.0, 'type': 'detector'},
        {'id': 'arrival_train0', 'type': 'arrival', 'offset': 19900, },
    ]
    assert points == expected


def test_point_switch_points_encountered_by_train1_reverse(
    use_case_point_switch
):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in use_case_point_switch.points_encountered_by_train(1)
    ]
    expected = [
        {'id': 'departure_train1', 'type': 'departure', 'offset': 0, },
        {'id': 'S2', 'type': 'signal', 'offset': 9750.0, },
        {'id': 'D2', 'type': 'detector', 'offset': 9770.0, },
        {'id': 'DVG', 'type': 'switch', 'offset': 9950.0, },
        {'id': 'D0', 'type': 'detector', 'offset': 10130.0, },
        {'id': 'arrival_train1', 'type': 'arrival', 'offset': 19900, },
    ]
    assert points == expected


def test_point_switch_space_time_chart(use_case_point_switch):

    ax = use_case_point_switch.space_time_chart(0, points_to_show=['switch'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == 19_900.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['DVG', ]
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()


def test_point_switch_tvd_blocks(use_case_point_switch):

    expected = {
        'D0<->buffer_stop.0': 'D0<->buffer_stop.0',
        'D0<->D1': 'DVG',
        'D1<->buffer_stop.1': 'D1<->buffer_stop.1',
        'D0<->D2': 'DVG',
        'D2<->buffer_stop.2': 'D2<->buffer_stop.2',
    }
    assert use_case_point_switch.tvd_blocks == expected


def test_point_switch_entry_signals(use_case_point_switch):

    expected = [
        {
            'D0<->buffer_stop.0': None,
            'DVG': 'S0',
            'D1<->buffer_stop.1': 'S0',
        },
        {
            'D2<->buffer_stop.2': None,
            'DVG': 'S2',
            'D0<->buffer_stop.0': 'S2'
        }
    ]
    assert use_case_point_switch.entry_signals == expected
