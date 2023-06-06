"""
use_case_station_capacity2
---------

                        station (2 tracks)

                          --------S1-D1-(T1)
                        /                    \
    --(T0)-------S0-D0-<(DVG)            (CVG)>-----------(T3)--->
                        \                    /
                          --------S2-D2-(T2)

All tracks are 1 km long
Train 0 starts from T0 at t=0s, stops at T1, and arrives at T3
Train 1 starts from T at t=60s, stops at T2, and arrives at T3
"""  # noqa

import matplotlib.pyplot as plt


def test_station_capacity2_infra(use_case_station_capacity2):
    assert isinstance(use_case_station_capacity2.infra, dict)


def test_station_capacity2_infra_routes(use_case_station_capacity2):
    assert set(use_case_station_capacity2.routes) == \
        set([
            'rt.buffer_stop.0->D0',
            'rt.D0->D1',
            'rt.D0->D2',
            'rt.D1->D3',
            'rt.D2->D3',
            'rt.D3->buffer_stop.1',
        ])


def test_station_capacity2_infra_route_switches(use_case_station_capacity2):
    assert use_case_station_capacity2.route_switches == \
        {
            'rt.D1->D3': 'CVG',
            'rt.D2->D3': 'CVG',
            'rt.D0->D1': 'DVG',
            'rt.D0->D2': 'DVG',
        }


def test_station_capacity2_infra_route_limits(use_case_station_capacity2):
    assert use_case_station_capacity2.route_limits == \
        {
            'D0': ('T0', 820.0),
            'D1': ('T1', 820.0),
            'D2': ('T2', 820.0),
            'D3': ('T3', 820.0),
            'buffer_stop.0': ('T0', 0.0),
            'buffer_stop.1': ('T3', 1000.0),
        }


def test_station_capacity2_infra_block_lengths(use_case_station_capacity2):
    assert use_case_station_capacity2.track_section_lengths == \
        {
            'T0': 1000.0,
            'T1': 1000.0,
            'T2': 1000.0,
            'T3': 1000.0,
        }


def test_station_capacity2_infra_route_lengths(use_case_station_capacity2):
    assert use_case_station_capacity2.route_lengths == \
        {
            'rt.buffer_stop.0->D0': 820.,
            'rt.D0->D1': 1000.,
            'rt.D0->D2': 1000.,
            'rt.D1->D3': 1000.,
            'rt.D2->D3': 1000.,
            'rt.D3->buffer_stop.1': 180.,
        }


def test_station_capacity2_infra_num_switches(use_case_station_capacity2):
    assert use_case_station_capacity2.num_switches == 2


def test_station_capacity2_infra_draw_infra_not_fail(use_case_station_capacity2):
    """Test if it does not raise an exception"""
    try:
        use_case_station_capacity2.draw_infra()
    except:  # noqa
        assert False


def test_station_capacity2_infra_points_of_interest(use_case_station_capacity2):
    poi = use_case_station_capacity2.points_of_interest
    assert set(poi.keys()) == {'CVG', 'DVG', 'station'}


def test_station_capacity2_infra_station_capacities(use_case_station_capacity2):
    assert (
        use_case_station_capacity2.station_capacities == {'station': 2}
    )


def test_station_capacity2_infra_num_stations(use_case_station_capacity2):
    assert use_case_station_capacity2.num_stations == 1


def test_station_capacity2_convergence_entry_signals(use_case_station_capacity2):
    assert use_case_station_capacity2.convergence_entry_signals == ['S1', 'S2']


def test_station_capacity2_points_on_tracks(use_case_station_capacity2):
    expected = {
        "T0": {
            "S0": (800, 'signal'),
            "D0": (820, 'detector'),
        },
        "T1": {
            "station": (790, 'station'),
            "S1": (800, 'signal'),
            "D1": (820, 'detector'),
        },
        "T2": {
            "station": (790, 'station'),
            "S2": (800, 'signal'),
            "D2": (820, 'detector'),
        },

        "T3": {
            "S3": (800, 'signal'),
            "D3": (820, 'detector'),
        },

    }

    assert use_case_station_capacity2.points_on_track_sections == expected


def test_station_capacity2_simulation_type(use_case_station_capacity2):
    assert isinstance(use_case_station_capacity2.simulation, dict)


def test_station_capacity2_simulation_num_trains(use_case_station_capacity2):
    assert use_case_station_capacity2.num_trains == 2


def test_station_capacity2_simulation_trains(use_case_station_capacity2):
    assert use_case_station_capacity2.trains == ['train0', 'train1']


def test_station_capacity2_simulation_departure_times(use_case_station_capacity2):
    assert use_case_station_capacity2.departure_times == [0, 60]


def test_station_capacity2_results_length(use_case_station_capacity2):
    assert len(use_case_station_capacity2.results) == use_case_station_capacity2.num_trains


def test_station_capacity2_results_train_track_sections(use_case_station_capacity2):
    assert use_case_station_capacity2.train_track_sections(0) == ['T0', 'T1', 'T3']
    assert use_case_station_capacity2.train_track_sections(1) == ['T0', 'T2', 'T3']


def test_station_capacity2_results_points_encountered_by_train(use_case_station_capacity2):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in use_case_station_capacity2.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'S0', 'type': 'signal', 'offset': 800.0},
        {'id': 'D0', 'type': 'detector', 'offset': 820.0},
        {'id': 'station', 'type': 'station', 'offset': 1790.0},
        {'id': 'S1', 'type': 'signal', 'offset': 1800.0},
        {'id': 'D1', 'type': 'detector', 'offset': 1820.0},
        {'id': 'S3', 'type': 'signal', 'offset': 2800.0},
        {'id': 'D3', 'type': 'detector', 'offset': 2820.0},

    ]
    assert points == expected


def test_station_capacity2_space_time_graph(use_case_station_capacity2):

    ax = use_case_station_capacity2.space_time_graph(0, types_to_show=['station'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 100.
    assert round(ax.dataLim.ymax) == 2980.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station', ]
    )
    assert ax.get_title() == "train0 (eco)"
    plt.close()
