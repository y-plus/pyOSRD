"""
osrd_cvg_dvg
---------
station0 (2 tracks)                        station1 (2 tracks)

        ┎S0                                      S4┐
(T0)-----D0-                                  --D4---------(T4)-->
              \   S2┐                   ┎S3  /
            CVG>-D2-----(T2)--+--(T3)----D3-<DVG
        ┎S1   /                              \   S5┐
(T1)-----D1-                                  --D5---------(T5)-->

All tracks are 500m long
Train 0 starts from T0 at t=0 and arrives at T4
Train 1 starts from T1 at t=100 and arrives at T5
"""  # noqa

import pytest
import matplotlib.pyplot as plt

from rlway.pyosrd.osrd import Point


def test_cvg_dvg_infra(use_case_cvg_dvg):
    assert isinstance(use_case_cvg_dvg.infra, dict)


def test_cvg_dvg_infra_routes(use_case_cvg_dvg):
    assert set(use_case_cvg_dvg.routes) == \
        set([
            'rt.buffer_stop.0->D0',
            'rt.D0->D3',
            'rt.buffer_stop.1->D1',
            'rt.D1->D3',
            'rt.D3->buffer_stop.2',
            'rt.D3->buffer_stop.3',
            'rt.buffer_stop.3->D5',
            'rt.D5->D2',
            'rt.buffer_stop.2->D4',
            'rt.D4->D2',
            'rt.D2->buffer_stop.0',
            'rt.D2->buffer_stop.1',
        ])


def test_cvg_dvg_infra_block_lengths(use_case_cvg_dvg):
    assert use_case_cvg_dvg.track_section_lengths == \
        {
            'T0': 500.,
            'T1': 500.,
            'T2': 500.,
            'T3': 500.,
            'T4': 500.,
            'T5': 500.,
        }


def test_cvg_dvg_infra_num_switches(use_case_cvg_dvg):
    assert use_case_cvg_dvg.num_switches == 2


def test_cvg_dvg_infra_draw_infra_not_fail(use_case_cvg_dvg):
    """Test if it does not raise an exception"""
    try:
        use_case_cvg_dvg.draw_infra_points()
    except:  # noqa
        assert False


def test_cvg_dvg_infra_station_capacities(use_case_cvg_dvg):
    assert (
        use_case_cvg_dvg.station_capacities == {'station0': 2, 'station1': 2}
    )


def test_cvg_dvg_infra_num_stations(use_case_cvg_dvg):
    assert use_case_cvg_dvg.num_stations == 2


def test_cvg_dvg_points_on_tracks(use_case_cvg_dvg):
    expected = {
        "T0": [
            Point(id='buffer_stop.0', track_section='T0', position=0.0, type='buffer_stop'),  # noqa
            Point(track_section='T0', id="station0", position=300, type='station'),  # noqa
            Point(track_section='T0', id="S0", position=430, type='signal'),  # noqa
            Point(track_section='T0', id="D0", position=450, type='detector'),  # noqa
            Point(track_section='T0', id="CVG", position=500, type='switch'),  # noqa
        ],
        "T1": [
            Point(id='buffer_stop.1', track_section='T1', position=0.0, type='buffer_stop'),  # noqa
            Point(track_section='T1', id="station0", position=300, type='station'),  # noqa
            Point(track_section='T1', id="S1", position=430, type='signal'),  # noqa
            Point(track_section='T1', id="D1", position=450, type='detector'),  # noqa
            Point(track_section='T1', id="CVG", position=500, type='switch'),  # noqa
        ],
        "T2": [
            Point(track_section='T2', id="CVG", position=0, type='switch'),  # noqa
            Point(track_section='T2', id="D2", position=50, type='detector'),  # noqa
            Point(track_section='T2', id="S2", position=70, type='signal'),  # noqa
            Point(id='L', track_section='T2', position=500, type="link"),  # noqa
        ],
        "T3": [
            Point(id='L', track_section='T3', position=0, type="link"),  # noqa
            Point(track_section='T3', id="S3", position=430, type='signal'),  # noqa
            Point(track_section='T3', id="D3", position=450, type='detector'),  # noqa
            Point(track_section='T3', id="DVG", position=500, type='switch'),  # noqa
        ],
        "T4": [
            Point(track_section='T4', id="DVG", position=0, type='switch'),  # noqa
            Point(track_section='T4', id="D4", position=50, type='detector'),  # noqa
            Point(track_section='T4', id="S4", position=70, type='signal'),  # noqa
            Point(track_section='T4', id="station1", position=480, type='station'),  # noqa
            Point(id='buffer_stop.2', track_section='T4', position=500.0, type='buffer_stop'),  # noqa
        ],
        "T5": [
            Point(track_section='T5', id="DVG", position=0, type='switch'),  # noqa
            Point(track_section='T5', id="D5", position=50, type='detector'),  # noqa
            Point(track_section='T5', id="S5", position=70, type='signal'),  # noqa
            Point(track_section='T5', id="station1", position=480, type='station'),  # noqa
            Point(id='buffer_stop.3', track_section='T5', position=500.0, type='buffer_stop'),  # noqa
        ],
    }

    assert use_case_cvg_dvg.points_on_track_sections() == expected


def test_cvg_dvg_simulation_type(use_case_cvg_dvg):
    assert isinstance(use_case_cvg_dvg.simulation, dict)


def test_cvg_dvg_simulation_num_trains(use_case_cvg_dvg):
    assert use_case_cvg_dvg.num_trains == 2


def test_cvg_dvg_simulation_trains(use_case_cvg_dvg):
    assert use_case_cvg_dvg.trains == ['train0', 'train1']


def test_cvg_dvg_simulation_departure_times(use_case_cvg_dvg):
    assert use_case_cvg_dvg.departure_times == [0, 100]


def test_cvg_dvg_run_arror(osrd_cvg_dvg_missing_sim):
    match = "Missing json file to run OSRD"
    with pytest.raises(ValueError, match=match):
        osrd_cvg_dvg_missing_sim.run()


def test_cvg_dvg_has_results(use_case_cvg_dvg):
    assert use_case_cvg_dvg.has_results


def test_cvg_dvg_has_no_results(osrd_cvg_dvg_before_run):
    assert not osrd_cvg_dvg_before_run.has_results


def test_cvg_dvg_results_length(use_case_cvg_dvg):
    assert len(use_case_cvg_dvg.results) == use_case_cvg_dvg.num_trains


def test_cvg_dvg_results_train_track_sections(use_case_cvg_dvg):
    assert use_case_cvg_dvg.train_track_sections(0) == [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'T2', 'direction': 'START_TO_STOP'},
        {'id': 'T3', 'direction': 'START_TO_STOP'},
        {'id': 'T4', 'direction': 'START_TO_STOP'},
    ]
    assert use_case_cvg_dvg.train_track_sections(1) == [
        {'id': 'T1', 'direction': 'START_TO_STOP'},
        {'id': 'T2', 'direction': 'START_TO_STOP'},
        {'id': 'T3', 'direction': 'START_TO_STOP'},
        {'id': 'T5', 'direction': 'START_TO_STOP'},
    ]


def test_cvg_dvg_results_pts_encountered_by_train(use_case_cvg_dvg):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in use_case_cvg_dvg.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'departure_train0', 'offset': 0.0, 'type': 'departure'},
        {'id': 'station0', 'offset': 0.0, 'type': 'station'},
        {'id': 'S0', 'offset': 130.0, 'type': 'signal'},
        {'id': 'D0', 'offset': 150.0, 'type': 'detector'},
        {'id': 'CVG', 'offset': 200.0, 'type': 'switch'},
        {'id': 'D2', 'offset': 250.0, 'type': 'detector'},
        {'id': 'S3', 'offset': 1130.0, 'type': 'signal'},
        {'id': 'D3', 'offset': 1150.0, 'type': 'detector'},
        {'id': 'DVG', 'offset': 1200.0, 'type': 'switch'},
        {'id': 'D4', 'offset': 1250.0, 'type': 'detector'},
        {'id': 'station1', 'offset': 1680.0, 'type': 'station'},
        {'id': 'arrival_train0', 'offset': 1690.0, 'type': 'arrival'},
    ]
    assert points == expected


def test_cvg_dvg_space_time_chart(use_case_cvg_dvg):

    ax = use_case_cvg_dvg.space_time_chart(0, points_to_show=['station'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == (500. - 300.) + 2 * 500. + 490.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station0', 'station1']
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()


def test_cvg_dvg_tvd_blocks(use_case_cvg_dvg):

    expected = {
        'D0<->buffer_stop.0': 'D0<->buffer_stop.0',
        'D0<->D2': 'CVG',
        'D2<->D3': 'D2<->D3',
        'D1<->buffer_stop.1': 'D1<->buffer_stop.1',
        'D1<->D2': 'CVG',
        'D3<->D4': 'DVG',
        'D4<->buffer_stop.2': 'D4<->buffer_stop.2',
        'D3<->D5': 'DVG',
        'D5<->buffer_stop.3': 'D5<->buffer_stop.3',
    }
    assert use_case_cvg_dvg.tvd_blocks == expected


def test_cvg_dvg_stop_positions(use_case_cvg_dvg):

    expected = [
        {
            'D0<->buffer_stop.0': {
                'type': 'station',
                'offset': 0.0,
                'id': 'station0'
            },
            'CVG': {'type': 'switch', 'offset': None},
            'D2<->D3': {'type': 'signal', 'offset': 1130.0, 'id': 'D2'},
            'DVG': {'type': 'switch', 'offset': None},
            'D4<->buffer_stop.2': {
                'type': 'station',
                'offset': 1680.0,
                'id': 'station1',
            }
        },
        {
            'D1<->buffer_stop.1': {
                'type': 'station',
                'offset': None,
                'id': 'station0',
            },
            'CVG': {'type': 'switch', 'offset': None},
            'D2<->D3': {'type': 'signal', 'offset': 1130.0, 'id': 'D2'},
            'DVG': {'type': 'switch', 'offset': None},
            'D5<->buffer_stop.3': {
                'type': 'station',
                'offset': None,
                'id': 'station1',
            }
        }
    ]

    assert use_case_cvg_dvg.stop_positions == expected
