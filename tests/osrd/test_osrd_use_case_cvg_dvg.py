"""
osrd_cvg_dvg
---------


station0 (2 tracks)                        station1 (2 tracks)

       ┎S0                                      S4┐
(T0)-----D0-                                  --D4---------(T4)-->
             \  S2┐                    ┎S3  /
           CVG>-D2-----(T2)--o--(T3)----D3-<DVG
       ┎S1   /                              \   S5┐
(T1)-----D1-                                  --D5---------(T5)-->

All tracks are 500m long
Train 0 starts from T0 at t=0 and arrives at T4
Train 1 starts from T1 at t=100 and arrives at T5
"""  # noqa

import pytest
import matplotlib.pyplot as plt


def testuse_case_cvg_dvg_infra(use_case_cvg_dvg):
    assert isinstance(use_case_cvg_dvg.infra, dict)


def testuse_case_cvg_dvg_infra_routes(use_case_cvg_dvg):
    assert set(use_case_cvg_dvg.routes) == \
        set([
            'rt.D0->D3',
            'rt.D1->D3',
            'rt.buffer_stop.0->D0',
            'rt.buffer_stop.1->D1',
            'rt.D3->D5',
            'rt.D3->D4',
            'rt.D4->buffer_stop.2',
            'rt.D5->buffer_stop.3',
        ])


def testuse_case_cvg_dvg_infra_route_switches(use_case_cvg_dvg):
    assert use_case_cvg_dvg.route_switches == \
        {
            'rt.D0->D3': 'CVG',
            'rt.D1->D3': 'CVG',
            'rt.D3->D5': 'DVG',
            'rt.D3->D4': 'DVG',
        }


def testuse_case_cvg_dvg_infra_route_limits(use_case_cvg_dvg):
    assert use_case_cvg_dvg.route_limits == \
        {
            'D0': ('T0', 450.0),
            'D1': ('T1', 450.0),
            'D3': ('T3', 450.0),
            'D4': ('T4', 450.0),
            'D5': ('T5', 450.0),
            'buffer_stop.0': ('T0', 0.0),
            'buffer_stop.1': ('T1', 0.0),
            'buffer_stop.2': ('T4', 500.0),
            'buffer_stop.3': ('T5', 500.0)
        }


def testuse_case_cvg_dvg_infra_block_lengths(use_case_cvg_dvg):
    assert use_case_cvg_dvg.track_section_lengths == \
        {
            'T0': 500.0,
            'T1': 500.0,
            'T2': 500.0,
            'T3': 500.0,
            'T4': 500.0,
            'T5': 500.0
        }


def testuse_case_cvg_dvg_infra_route_lengths(use_case_cvg_dvg):
    assert use_case_cvg_dvg.route_lengths == \
        {
            'rt.D0->D3': 1000.0,
            'rt.buffer_stop.0->D0': 450.0,
            'rt.D1->D3': 1000.0,
            'rt.buffer_stop.1->D1': 450.0,
            'rt.D3->D5': 500.0,
            'rt.D3->D4': 500.0,
            'rt.D4->buffer_stop.2': 50.0,
            'rt.D5->buffer_stop.3': 50.0
        }


def testuse_case_cvg_dvg_infra_num_switches(use_case_cvg_dvg):
    assert use_case_cvg_dvg.num_switches == 2


def testuse_case_cvg_dvg_infra_draw_infra_not_fail(use_case_cvg_dvg):
    """Test if it does not raise an exception"""
    try:
        use_case_cvg_dvg.draw_infra()
    except:  # noqa
        assert False


def testuse_case_cvg_dvg_infra_points_of_interest(use_case_cvg_dvg):
    poi = use_case_cvg_dvg.points_of_interest
    assert set(poi.keys()) == {'CVG', 'DVG', 'station0', 'station1'}


def testuse_case_cvg_dvg_infra_station_capacities(use_case_cvg_dvg):
    assert (
        use_case_cvg_dvg.station_capacities == {'station0': 2, 'station1': 2}
    )


def testuse_case_cvg_dvg_infra_num_stations(use_case_cvg_dvg):
    assert use_case_cvg_dvg.num_stations == 2


def testuse_case_cvg_dvg_points_on_tracks(use_case_cvg_dvg):
    expected = {
        "T0": {
            "station0": (300, 'station'),
            "S0": (430, 'signal'),
            "D0": (450, 'detector'),
            "CVG": (500, 'switch', 'point'),
        },
        "T1": {
            "station0": (300, 'station'),
            "S1": (430, 'signal'),
            "D1": (450, 'detector'),
            "CVG": (500, 'switch', 'point'),
        },
        "T2": {
            "CVG": (0, 'switch', 'point'),
        },
        "T3": {
            "S3": (430, 'signal'),
            "D3": (450, 'detector'),
            "DVG": (500, 'switch', 'point'),
        },
        "T4": {
            "DVG": (0, 'switch', 'point'),
            "S4": (430, 'signal'),
            "D4": (450, 'detector'),
            "station1": (480, 'station'),
        },
        "T5": {
            "DVG": (0, 'switch', 'point'),
            "S5": (430, 'signal'),
            "D5": (450, 'detector'),
            "station1": (480, 'station'),
        },
    }

    assert use_case_cvg_dvg.points_on_track_sections == expected


def test_use_case_divergence_route_tvds(use_case_divergence):
    expected = {
            # TODO
        }
    assert use_case_divergence.route_tvds == expected


def testuse_case_cvg_dvg_simulation_type(use_case_cvg_dvg):
    assert isinstance(use_case_cvg_dvg.simulation, dict)


def testuse_case_cvg_dvg_simulation_num_trains(use_case_cvg_dvg):
    assert use_case_cvg_dvg.num_trains == 2


def testuse_case_cvg_dvg_simulation_trains(use_case_cvg_dvg):
    assert use_case_cvg_dvg.trains == ['train0', 'train1']


def testuse_case_cvg_dvg_simulation_departure_times(use_case_cvg_dvg):
    assert use_case_cvg_dvg.departure_times == [0, 100]


def testuse_case_cvg_dvg_run_arror(osrd_cvg_dvg_missing_sim):
    match = "Missing json file to run OSRD"
    with pytest.raises(ValueError, match=match):
        osrd_cvg_dvg_missing_sim.run()


def testuse_case_cvg_dvg_has_results(use_case_cvg_dvg):
    assert use_case_cvg_dvg.has_results


def testuse_case_cvg_dvg_has_no_results(osrd_cvg_dvg_before_run):
    assert not osrd_cvg_dvg_before_run.has_results


def testuse_case_cvg_dvg_results_length(use_case_cvg_dvg):
    assert len(use_case_cvg_dvg.results) == use_case_cvg_dvg.num_trains


def testuse_case_cvg_dvg_results_train_track_sections(use_case_cvg_dvg):
    assert use_case_cvg_dvg.train_track_sections(0) == {
        'T0': 'START_TO_STOP',
        'T2': 'START_TO_STOP',
        'T3': 'START_TO_STOP',
        'T4': 'START_TO_STOP',
    }
    assert use_case_cvg_dvg.train_track_sections(1) == {
        'T1': 'START_TO_STOP',
        'T2': 'START_TO_STOP',
        'T3': 'START_TO_STOP',
        'T5': 'START_TO_STOP',
    }


def testuse_case_cvg_dvg_results_points_encountered_by_train(use_case_cvg_dvg):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in use_case_cvg_dvg.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'DEPARTURE', 'type': 'start', 'offset': 300.0, },
        {'id': 'station0', 'type': 'station', 'offset': 300.0},
        {'id': 'S0', 'type': 'signal', 'offset': 430.0},
        {'id': 'D0', 'type': 'detector', 'offset': 450.0},
        {'id': 'CVG', 'type': 'switch', 'offset': 500.0},
        {'id': 'S3', 'type': 'signal', 'offset': 1430.0},
        {'id': 'D3', 'type': 'detector', 'offset': 1450.0},
        {'id': 'DVG', 'type': 'switch', 'offset': 1500.0},
        {'id': 'END', 'type': 'end', 'offset': 1680.0, },
        {'id': 'S4', 'type': 'signal', 'offset': 1930.0},
        {'id': 'D4', 'type': 'detector', 'offset': 1950.0},
        {'id': 'station1', 'type': 'station', 'offset': 1980.0},

    ]
    assert points == expected


def testuse_case_cvg_dvg_space_time_graph(use_case_cvg_dvg):

    ax = use_case_cvg_dvg.space_time_graph(0, types_to_show=['station'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 300.
    assert round(ax.dataLim.ymax) == 1980.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station0', 'station1']
    )
    assert ax.get_title() == "train0 (eco)"
    plt.close()
