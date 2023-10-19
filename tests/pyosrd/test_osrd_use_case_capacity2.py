"""
use_case_station_capacity2

                                 o = station(2 lanes)
                     S1┐          ┎S3
                    -D1-(T1)---+-o-D3-(T3)
              ┎S0  /                       \   S5┐
    --(T0)-----D0-<DVG                   CVG>--D5-------(T5)--->
                   \  S2┐          ┎S4     /
                     -D2-(T2)---+-o-D4-(T4)

All tracks are 1 km long
Train 0 starts from T0 at t=0s, stops at T3, and arrives at T5
Train 1 starts from T0 at t=300s, stops at T4, and arrives at T5
"""  # noqa

import matplotlib.pyplot as plt

from rlway.pyosrd.osrd import Point


def test_station_capacity2_infra(use_case_station_capacity2):
    assert isinstance(use_case_station_capacity2.infra, dict)


def test_station_capacity2_infra_routes(use_case_station_capacity2):
    assert set(use_case_station_capacity2.routes) == \
        set([
            'rt.buffer_stop.0->D0',
            'rt.D0->D3',
            'rt.D0->D4',
            'rt.D1->buffer_stop.0',
            'rt.D2->buffer_stop.0',
            'rt.D3->buffer_stop.5',
            'rt.D4->buffer_stop.5',
            'rt.buffer_stop.5->D5',
            'rt.D5->D1',
            'rt.D5->D2',
        ])


def test_station_capacity2_infra_block_lengths(use_case_station_capacity2):
    assert use_case_station_capacity2.track_section_lengths == \
        {
            'T0': 1000.0,
            'T1': 1000.0,
            'T2': 1000.0,
            'T3': 1000.0,
            'T4': 1000.0,
            'T5': 1000.0,
        }


def test_station_capacity2_infra_num_switches(use_case_station_capacity2):
    assert use_case_station_capacity2.num_switches == 2


def test_station_capacity2_infra_draw_infra_not_fail(
    use_case_station_capacity2
):
    """Test if it does not raise an exception"""
    try:
        use_case_station_capacity2.draw_infra_points()
    except:  # noqa
        assert False


def test_station_capacity2_infra_station_capacities(
    use_case_station_capacity2
):
    assert (
        use_case_station_capacity2.station_capacities == {'station': 2}
    )


def test_station_capacity2_infra_num_stations(use_case_station_capacity2):
    assert use_case_station_capacity2.num_stations == 1


def test_station_capacity2_points_on_tracks(use_case_station_capacity2):
    expected = {
        "T0": [
            Point(id='buffer_stop.0', track_section='T0', position=0.0, type='buffer_stop'),  # noqa
            Point(id='S0', track_section='T0', position=800.0, type="signal"),  # noqa
            Point(id='D0', track_section='T0', position=820.0, type="detector"),  # noqa
            Point(id='DVG', track_section='T0', position=1000.0, type="switch"),  # noqa
        ],
        "T1": [
            Point(id='DVG', track_section='T1', position=0, type="switch"),  # noqa
            Point(id='D1', track_section='T1', position=180.0, type="detector"),  # noqa
            Point(id='S1', track_section='T1', position=200.0, type="signal"),  # noqa
            Point(id='L1-3', track_section='T1', position=1000.0, type="link"),  # noqa
        ],
        "T2": [
            Point(id='DVG', track_section='T2', position=0, type="switch"),  # noqa
            Point(id='D2', track_section='T2', position=180.0, type="detector"),  # noqa
            Point(id='S2', track_section='T2', position=200.0, type="signal"),  # noqa
            Point(id='L2-4', track_section='T2', position=1000.0, type="link"),  # noqa
        ],
        "T3": [
            Point(id='L1-3', track_section='T3', position=0, type="link"),  # noqa
            Point(id='station', track_section='T3', position=790.0, type="station"),  # noqa
            Point(id='S3', track_section='T3', position=800.0, type="signal"),  # noqa
            Point(id='D3', track_section='T3', position=820.0, type="detector"),  # noqa
            Point(id='CVG', track_section='T3', position=1000.0, type="switch"),  # noqa
        ],
        "T4": [
            Point(id='L2-4', track_section='T4', position=0, type="link"),  # noqa
            Point(id='station', track_section='T4', position=790.0, type="station"),  # noqa
            Point(id='S4', track_section='T4', position=800.0, type="signal"),  # noqa
            Point(id='D4', track_section='T4', position=820.0, type="detector"),  # noqa
            Point(id='CVG', track_section='T4', position=1000.0, type="switch"),  # noqa
        ],
        "T5": [
            Point(id='CVG', track_section='T5', position=0, type="switch"),  # noqa
            Point(id='D5', track_section='T5', position=180.0, type="detector"),  # noqa
            Point(id='S5', track_section='T5', position=200.0, type="signal"),  # noqa
            Point(id='buffer_stop.5', track_section='T5', position=1000.0, type='buffer_stop'),  # noqa
        ],
    }

    assert use_case_station_capacity2.points_on_track_sections() == expected


def test_station_capacity2_simulation_type(use_case_station_capacity2):
    assert isinstance(use_case_station_capacity2.simulation, dict)


def test_station_capacity2_simulation_num_trains(use_case_station_capacity2):
    assert use_case_station_capacity2.num_trains == 2


def test_station_capacity2_simulation_trains(use_case_station_capacity2):
    assert use_case_station_capacity2.trains == ['train0', 'train1']


def test_station_capacity2_simulation_departure_times(
    use_case_station_capacity2
):
    assert use_case_station_capacity2.departure_times == [0, 300.]


def test_station_capacity2_results_length(use_case_station_capacity2):
    num_trains = use_case_station_capacity2.num_trains
    assert len(use_case_station_capacity2.results) == num_trains


def test_station_capacity2_results_train_track_sections(
    use_case_station_capacity2
):
    tracks_0 = [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'T1', 'direction': 'START_TO_STOP'},
        {'id': 'T3', 'direction': 'START_TO_STOP'},
        {'id': 'T5', 'direction': 'START_TO_STOP'},
    ]
    assert use_case_station_capacity2.train_track_sections(0) == tracks_0
    tracks_1 = [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'T2', 'direction': 'START_TO_STOP'},
        {'id': 'T4', 'direction': 'START_TO_STOP'},
        {'id': 'T5', 'direction': 'START_TO_STOP'},
    ]
    assert use_case_station_capacity2.train_track_sections(1) == tracks_1


def test_station_capacity2_results_points_encountered_by_train(
    use_case_station_capacity2
):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in use_case_station_capacity2.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'departure_train0', 'offset': 0.0, 'type': 'departure'},
        {'id': 'S0', 'offset': 790.0, 'type': 'signal'},
        {'id': 'D0', 'offset': 810.0, 'type': 'detector'},
        {'id': 'DVG', 'offset': 990.0, 'type': 'switch'},
        {'id': 'D1', 'offset': 1170.0, 'type': 'detector'},
        {'id': 'station', 'offset': 2780.0, 'type': 'station'},
        {'id': 'S3', 'offset': 2790.0, 'type': 'signal'},
        {'id': 'D3', 'offset': 2810.0, 'type': 'detector'},
        {'id': 'CVG', 'offset': 2990.0, 'type': 'switch'},
        {'id': 'D5', 'offset': 3170.0, 'type': 'detector'},
        {'id': 'arrival_train0', 'offset': 3980.0, 'type': 'arrival'},
    ]
    assert expected == points


def test_station_capacity2_space_time_chart(use_case_station_capacity2):

    ax = use_case_station_capacity2.space_time_chart(
        0,
        points_to_show=['station']
    )

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == 3980.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station', ]
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()


def test_station_capacity2_blocks(use_case_station_capacity2):

    expected = {
        'D0<->buffer_stop.0': 'D0<->buffer_stop.0',
        'D0<->D1': 'DVG',
        'D1<->D3': 'D1<->D3',
        'D0<->D2': 'DVG',
        'D2<->D4': 'D2<->D4',
        'D3<->D5': 'CVG',
        'D5<->buffer_stop.5': 'D5<->buffer_stop.5',
        'D4<->D5': 'CVG',
    }
    assert use_case_station_capacity2.tvd_blocks == expected
