"""
osrd_case
---------


station0 (2 tracks)                        station1 (2 tracks)

(T0)--S0-D0-                               -S4-D4-(T4)-->
            |                             |
        (CVG)>-(T2)-S2-D2--o--S3-D3-(T3)-<(DVG)
            |                             |
(T1)--S1-D1-                               -S5-D5-(T5)-->

All tracks are 500m long
Train 0 starts from T0 at t=0 and arrives at T4
Train 1 starts from T1 at t=100 and arrives at T5
"""

import pytest
import matplotlib.pyplot as plt


def test_osrd_infra(osrd_case):
    assert isinstance(osrd_case.infra, dict)


def test_osrd_infra_routes(osrd_case):
    assert set(osrd_case.routes) == \
        set([
            'rt.D0->D2',
            'rt.buffer_stop.0->D0',
            'rt.D1->D2',
            'rt.buffer_stop.1->D1',
            'rt.D2->D3',
            'rt.D3->D5',
            'rt.D3->D4',
            'rt.D4->buffer_stop.2',
            'rt.D5->buffer_stop.3',
        ])


def test_osrd_infra_route_switches(osrd_case):
    assert osrd_case.route_switches == \
        {
            'rt.D0->D2': 'CVG',
            'rt.D1->D2': 'CVG',
            'rt.D3->D5': 'DVG',
            'rt.D3->D4': 'DVG',
        }


def test_osrd_infra_route_limits(osrd_case):
    assert osrd_case.route_limits == \
        {
            'D0': ('T0', 450.0),
            'D1': ('T1', 450.0),
            'D2': ('T2', 50.0),
            'D3': ('T3', 450.0),
            'D4': ('T4', 50.0),
            'D5': ('T5', 50.0),
            'buffer_stop.0': ('T0', 0.0),
            'buffer_stop.1': ('T1', 0.0),
            'buffer_stop.2': ('T4', 500.0),
            'buffer_stop.3': ('T5', 500.0)
        }


def test_osrd_infra_track_section_lengths(osrd_case):
    assert osrd_case.track_section_lengths == \
        {
            'T0': 500.0,
            'T1': 500.0,
            'T2': 500.0,
            'T3': 500.0,
            'T4': 500.0,
            'T5': 500.0
        }


def test_osrd_infra_route_lengths(osrd_case):
    assert osrd_case.route_lengths == \
        {
            'rt.D0->D2': 100.0,
            'rt.buffer_stop.0->D0': 450.0,
            'rt.D1->D2': 100.0,
            'rt.buffer_stop.1->D1': 450.0,
            'rt.D2->D3': 900.0,
            'rt.D3->D5': 100.0,
            'rt.D3->D4': 100.0,
            'rt.D4->buffer_stop.2': 450.0,
            'rt.D5->buffer_stop.3': 450.0
        }


def test_osrd_infra_num_switches(osrd_case):
    assert osrd_case.num_switches == 2


def test_osrd_infra_draw_infra_not_fail(osrd_case):
    """Test if it does not raise an exception"""
    try:
        osrd_case.draw_infra()
    except:  # noqa
        assert False


def test_osrd_infra_points_of_interest(osrd_case):
    poi = osrd_case.points_of_interest
    assert set(poi.keys()) == {'CVG', 'DVG', 'station0', 'station1'}


def test_osrd_infra_station_capacities(osrd_case):
    assert (
        osrd_case.station_capacities == {'station0': 2, 'station1': 2}
    )


def test_osrd_infra_num_stations(osrd_case):
    assert osrd_case.num_stations == 2


def test_osrd_convergence_entry_signals(osrd_case):
    assert osrd_case.convergence_entry_signals == ['S0', 'S1']


def test_osrd_points_on_tracks(osrd_case):
    expected = {
        "T0": {
            "station0": (300, 'station'),
            "S0": (430, 'cvg_signal'),
            "D0": (450, 'detector'),
        },
        "T1": {
            "station0": (300, 'station'),
            "S1": (430, 'cvg_signal'),
            "D1": (450, 'detector'),
        },
        "T2": {
            "S2": (30, 'signal'),
            "D2": (50, 'detector'),
        },
        "T3": {
            "S3": (430, 'signal'),
            "D3": (450, 'detector'),
        },
        "T4": {
            "S4": (30, 'signal'),
            "D4": (50, 'detector'),
            "station1": (300, 'station'),
        },
        "T5": {
            "S5": (30, 'signal'),
            "D5": (50, 'detector'),
            "station1": (300, 'station'),
        },
    }

    assert osrd_case.points_on_track_sections == expected


def test_osrd_simulation_type(osrd_case):
    assert isinstance(osrd_case.simulation, dict)


def test_osrd_simulation_num_trains(osrd_case):
    assert osrd_case.num_trains == 2


def test_osrd_simulation_trains(osrd_case):
    assert osrd_case.trains == ['train0', 'train1']


def test_osrd_simulation_departure_times(osrd_case):
    assert osrd_case.departure_times == [0, 100]


def test_osrd_run_arror(osrd_case_missing_sim):
    match = "Missing json file to run OSRD"
    with pytest.raises(ValueError, match=match):
        osrd_case_missing_sim.run()


def test_osrd_has_results(osrd_case):
    assert osrd_case.has_results


def test_osrd_has_no_results(osrd_case_before_run):
    assert not osrd_case_before_run.has_results


def test_osrd_results_length(osrd_case):
    assert len(osrd_case.results) == osrd_case.num_trains


def test_osrd_results_train_track_sections(osrd_case):
    assert osrd_case.train_track_sections(0) == ['T0', 'T2', 'T3', 'T4']
    assert osrd_case.train_track_sections(1) == ['T1', 'T2', 'T3', 'T5']


def test_osrd_results_points_encountered_by_train(osrd_case):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in osrd_case.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'station0', 'type': 'station', 'offset': 300.0},
        {'id': 'S0', 'type': 'cvg_signal', 'offset': 430.0},
        {'id': 'D0', 'type': 'detector', 'offset': 450.0},
        {'id': 'S2', 'type': 'signal', 'offset': 530.0},
        {'id': 'D2', 'type': 'detector', 'offset': 550.0},
        {'id': 'S3', 'type': 'signal', 'offset': 1430.0},
        {'id': 'D3', 'type': 'detector', 'offset': 1450.0},
        {'id': 'S4', 'type': 'signal', 'offset': 1530.0},
        {'id': 'D4', 'type': 'detector', 'offset': 1550.0},
        {'id': 'station1', 'type': 'station', 'offset': 1800.0},
    ]
    assert points == expected


def test_osrd_space_time_graph(osrd_case):

    ax = osrd_case.space_time_graph(0, types_to_show=['station'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 300.
    assert round(ax.dataLim.ymax) == 1800.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station0', 'station1']
    )
    assert ax.get_title() == "train0 (eco)"
    plt.close()
