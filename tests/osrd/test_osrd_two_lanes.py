"""
osrd_two_lanes
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


def test_osrd_2_lanes_infra(osrd_two_lanes):
    assert isinstance(osrd_two_lanes.infra, dict)


def test_osrd_2_lanes_infra_routes(osrd_two_lanes):
    assert set(osrd_two_lanes.routes) == \
        set([
            'rt.buffer_stop.4->D0',
            'rt.D0->D1',
            'rt.D0->D2',
            'rt.D1->D3',
            'rt.D2->D3',
            'rt.D3->buffer_stop.5',
        ])


def test_osrd_2_lanes_infra_route_switches(osrd_two_lanes):
    assert osrd_two_lanes.route_switches == \
        {
            'rt.D1->D3': 'CVG',
            'rt.D2->D3': 'CVG',
            'rt.D0->D1': 'DVG',
            'rt.D0->D2': 'DVG',
        }


def test_osrd_2_lanes_infra_route_limits(osrd_two_lanes):
    assert osrd_two_lanes.route_limits == \
        {
            'D0': ('T0', 820.0),
            'D1': ('T1', 820.0),
            'D2': ('T2', 820.0),
            'D3': ('T3', 820.0),
            'buffer_stop.4': ('T0', 0.0),
            'buffer_stop.5': ('T3', 1000.0),
        }


def test_osrd_2_lanes_infra_block_lengths(osrd_two_lanes):
    assert osrd_two_lanes.track_section_lengths == \
        {
            'T0': 1000.0,
            'T1': 1000.0,
            'T2': 1000.0,
            'T3': 1000.0,
        }


def test_osrd_2_lanes_infra_route_lengths(osrd_two_lanes):
    assert osrd_two_lanes.route_lengths == \
        {
            'rt.buffer_stop.4->D0': 820.,
            'rt.D0->D1': 1000.,
            'rt.D0->D2': 1000.,
            'rt.D1->D3': 1000.,
            'rt.D2->D3': 1000.,
            'rt.D3->buffer_stop.5': 180.,
        }


def test_osrd_2_lanes_infra_num_switches(osrd_two_lanes):
    assert osrd_two_lanes.num_switches == 2


def test_osrd_2_lanes_infra_draw_infra_not_fail(osrd_two_lanes):
    """Test if it does not raise an exception"""
    try:
        osrd_two_lanes.draw_infra()
    except:  # noqa
        assert False


def test_osrd_2_lanes_infra_points_of_interest(osrd_two_lanes):
    poi = osrd_two_lanes.points_of_interest
    assert set(poi.keys()) == {'CVG', 'DVG', 'station'}


def test_osrd_2_lanes_infra_station_capacities(osrd_two_lanes):
    assert (
        osrd_two_lanes.station_capacities == {'station': 2}
    )


def test_osrd_2_lanes_infra_num_stations(osrd_two_lanes):
    assert osrd_two_lanes.num_stations == 1


def test_osrd_2_lanes_convergence_entry_signals(osrd_two_lanes):
    assert osrd_two_lanes.convergence_entry_signals == ['S1', 'S2']


def test_osrd_2_lanes_points_on_tracks(osrd_two_lanes):
    expected = {
        "T0": {
            "S0": (800, 'signal'),
            "D0": (820, 'detector'),
        },
        "T1": {
            "station": (790, 'station'),
            "S1": (800, 'cvg_signal'),
            "D1": (820, 'detector'),
        },
        "T2": {
            "station": (790, 'station'),
            "S2": (800, 'cvg_signal'),
            "D2": (820, 'detector'),
        },

        "T3": {
            "S3": (800, 'signal'),
            "D3": (820, 'detector'),
        },

    }

    assert osrd_two_lanes.points_on_track_sections == expected


def test_osrd_2_lanes_simulation_type(osrd_two_lanes):
    assert isinstance(osrd_two_lanes.simulation, dict)


def test_osrd_2_lanes_simulation_num_trains(osrd_two_lanes):
    assert osrd_two_lanes.num_trains == 2


def test_osrd_2_lanes_simulation_trains(osrd_two_lanes):
    assert osrd_two_lanes.trains == ['train0', 'train1']


def test_osrd_2_lanes_simulation_departure_times(osrd_two_lanes):
    assert osrd_two_lanes.departure_times == [0, 60]


def test_osrd_2_lanes_results_length(osrd_two_lanes):
    assert len(osrd_two_lanes.results) == osrd_two_lanes.num_trains


def test_osrd_2_lanes_results_train_track_sections(osrd_two_lanes):
    assert osrd_two_lanes.train_track_sections(0) == ['T0', 'T1', 'T3']
    assert osrd_two_lanes.train_track_sections(1) == ['T0', 'T2', 'T3']


def test_osrd_2_lanes_results_points_encountered_by_train(osrd_two_lanes):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in osrd_two_lanes.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'S0', 'type': 'signal', 'offset': 800.0},
        {'id': 'D0', 'type': 'detector', 'offset': 820.0},
        {'id': 'station', 'type': 'station', 'offset': 1790.0},
        {'id': 'S1', 'type': 'cvg_signal', 'offset': 1800.0},
        {'id': 'D1', 'type': 'detector', 'offset': 1820.0},
        {'id': 'S3', 'type': 'signal', 'offset': 2800.0},
        {'id': 'D3', 'type': 'detector', 'offset': 2820.0},

    ]
    assert points == expected


def test_osrd_2_lanes_space_time_graph(osrd_two_lanes):

    ax = osrd_two_lanes.space_time_graph(0, types_to_show=['station'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 100.
    assert round(ax.dataLim.ymax) == 2980.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station', ]
    )
    assert ax.get_title() == "train0 (eco)"
    plt.close()
