"""
use_case_station_capacity2
---------

                                o = station(2 lanes)
                    S1s┐           ┎S1e
                    -D1s-(T1)---o---D1e--
         ┎S0e     /                       \   S3s┐
--(T0)----D0e----<DVG                   CVG>--D3s----(T3)---
                  \  S2s┐          ┎S2e   /
                    -D2s-(T2)---o---D2e--

All tracks are 1 km long
Train 0 starts from T0 at t=0s, stops at T1, and arrives at T3
Train 1 starts from T0 at t=300s, stops at T2, and arrives at T3
"""  # noqa

import matplotlib.pyplot as plt


def test_station_capacity2_infra(use_case_station_capacity2):
    assert isinstance(use_case_station_capacity2.infra, dict)


def test_station_capacity2_infra_routes(use_case_station_capacity2):
    assert set(use_case_station_capacity2.routes) == \
        set([
            'rt.buffer_stop.0->D0e',
            'rt.D0e->D2e',
            'rt.D2e->buffer_stop.1',
            'rt.D0e->D1e',
            'rt.D1e->buffer_stop.1',
            'rt.buffer_stop.1->D3s',
            'rt.D3s->D2e',
            'rt.D3s->D1e',
            'rt.D1e->buffer_stop.0',
            'rt.D2e->buffer_stop.0',
        ])


def test_station_capacity2_infra_route_switches(use_case_station_capacity2):
    assert use_case_station_capacity2.route_switches == \
        {
            'rt.D0e->D2e': 'DVG',
            'rt.D0e->D1e': 'DVG',
            'rt.D1e->buffer_stop.1': 'CVG',
            'rt.D1e->buffer_stop.0': 'DVG',
            'rt.D2e->buffer_stop.1': 'CVG',
            'rt.D2e->buffer_stop.0': 'DVG',
            'rt.D3s->D2e': 'CVG',
            'rt.D3s->D1e': 'CVG',
        }


def test_station_capacity2_infra_route_limits(use_case_station_capacity2):
    assert use_case_station_capacity2.route_limits == \
        {
            'D0e': ('T0', 820.0),
            'D1s': ('T1', 180.0),
            'D1e': ('T1', 820.0),
            'D2s': ('T2', 180.0),
            'D2e': ('T2', 820.0),
            'D3s': ('T3', 180.0),
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
            'rt.D0e->D2e': 1000.0,
            'rt.D0e->D1e': 1000.0,
            'rt.buffer_stop.0->D0e': 820.0,
            'rt.D1e->buffer_stop.1': 1180.0,
            'rt.D1e->buffer_stop.0': 180.0,
            'rt.D2e->buffer_stop.1': 1180.0,
            'rt.D2e->buffer_stop.0': 180.0,
            'rt.D3s->D2e': 1640.0,
            'rt.D3s->D1e': 1640.0,
            'rt.buffer_stop.1->D3s': 820.0
        }


def test_station_capacity2_infra_num_switches(use_case_station_capacity2):
    assert use_case_station_capacity2.num_switches == 2


def test_station_capacity2_infra_draw_infra_not_fail(
    use_case_station_capacity2
):
    """Test if it does not raise an exception"""
    try:
        use_case_station_capacity2.draw_infra()
    except:  # noqa
        assert False


def test_station_capacity2_infra_points_of_interest(
    use_case_station_capacity2
):
    poi = use_case_station_capacity2.points_of_interest
    assert set(poi.keys()) == {'CVG', 'DVG', 'station'}


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
        "T0": {
            "S0": (800, 'signal'),
            "D0": (820, 'detector'),
            "DVG": (1000.0, 'switch', 'point'),
        },
        "T1": {
            "DVG": (0.0, 'switch', 'point'),
            "station": (790, 'station'),
            "S1": (800, 'signal'),
            "D1": (820, 'detector'),
            "CVG": (1000.0, 'switch', 'point'),
        },
        "T2": {
            "DVG": (0.0, 'switch', 'point'),
            "station": (790, 'station'),
            "S2": (800, 'signal'),
            "D2": (820, 'detector'),
            "CVG": (1000.0, 'switch', 'point'),
        },
        "T3": {
            "CVG": (0.0, 'switch', 'point'),
            "S3": (800, 'signal'),
            "D3": (820, 'detector'),
        },

    }

    assert use_case_station_capacity2.points_on_track_sections == expected


def test_use_case_point_switch_route_tvds(use_case_point_switch):
    expected = {
            # TODO
        }
    assert use_case_point_switch.route_tvds == expected


def test_station_capacity2_simulation_type(use_case_station_capacity2):
    assert isinstance(use_case_station_capacity2.simulation, dict)


def test_station_capacity2_simulation_num_trains(use_case_station_capacity2):
    assert use_case_station_capacity2.num_trains == 2


def test_station_capacity2_simulation_trains(use_case_station_capacity2):
    assert use_case_station_capacity2.trains == ['train0', 'train1']


def test_station_capacity2_simulation_departure_times(
    use_case_station_capacity2
):
    assert use_case_station_capacity2.departure_times == [0, 60]


def test_station_capacity2_results_length(use_case_station_capacity2):
    num_trains = use_case_station_capacity2.num_trains
    assert len(use_case_station_capacity2.results) == num_trains


def test_station_capacity2_results_train_track_sections(
    use_case_station_capacity2
):
    tracks_0 = {
        'T0': 'START_TO_STOP',
        'T1': 'START_TO_STOP',
        'T3': 'START_TO_STOP',
    }
    assert use_case_station_capacity2.train_track_sections(0) == tracks_0
    tracks_1 = {
        'T0': 'START_TO_STOP',
        'T2': 'START_TO_STOP',
        'T3': 'START_TO_STOP',
    }
    assert use_case_station_capacity2.train_track_sections(1) == tracks_1


def test_station_capacity2_results_points_encountered_by_train(
    use_case_station_capacity2
):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in use_case_station_capacity2.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'DEPARTURE', 'type': 'departure', 'offset': 100.0, },
        {'id': 'S0', 'type': 'signal', 'offset': 800.0},
        {'id': 'D0', 'type': 'detector', 'offset': 820.0},
        {'id': 'DVG', 'type': 'switch', 'offset': 1000.0},
        {'id': 'station', 'type': 'station', 'offset': 1790.0},
        {'id': 'S1', 'type': 'signal', 'offset': 1800.0},
        {'id': 'D1', 'type': 'detector', 'offset': 1820.0},
        {'id': 'CVG', 'type': 'switch', 'offset': 2000.0},
        {'id': 'S3', 'type': 'signal', 'offset': 2800.0},
        {'id': 'D3', 'type': 'detector', 'offset': 2820.0},
        {'id': 'ARRIVAL', 'type': 'arrival', 'offset': 2880.0, },
    ]
    assert expected == points


def test_station_capacity2_space_time_graph(use_case_station_capacity2):

    ax = use_case_station_capacity2.space_time_graph(
        0,
        types_to_show=['station']
    )

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 100.
    assert round(ax.dataLim.ymax) == 2980.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station', ]
    )
    assert ax.get_title() == "train0 (eco)"
    plt.close()
