"""
divergence
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


import matplotlib.pyplot as plt


def test_use_case_divergence_infra(use_case_divergence):
    assert isinstance(use_case_divergence.infra, dict)


def test_use_case_divergence_infra_routes(use_case_divergence):
    assert set(use_case_divergence.routes) == \
        set([
            'rt.D0->buffer_stop.2',
            'rt.D0->buffer_stop.1',
            'rt.buffer_stop.0->D0',
            'rt.D1->buffer_stop.0',
            'rt.buffer_stop.1->D1',
            'rt.D2->buffer_stop.0',
            'rt.buffer_stop.2->D2'
        ])


def test_use_case_divergence_infra_route_switches(use_case_divergence):
    assert use_case_divergence.route_switches == \
        {
            'rt.D0->buffer_stop.2': 'DVG',
            'rt.D0->buffer_stop.1': 'DVG',
            'rt.D1->buffer_stop.0': 'DVG',
            'rt.D2->buffer_stop.0': 'DVG'
        }


def test_use_case_divergence_infra_route_limits(use_case_divergence):
    assert use_case_divergence.route_limits == \
        {
            'D0': ('T0', 9820.0),
            'D1': ('T1', 180.0),
            'D2': ('T2', 180.0),
            'buffer_stop.0': ('T0', 0.0),
            'buffer_stop.1': ('T1', 10_000.0),
            'buffer_stop.2': ('T2', 10_000.0),
        }


def test_use_case_divergence_infra_track_lengths(use_case_divergence):
    assert use_case_divergence.track_section_lengths == \
        {
            'T0': 10_000.0,
            'T1': 10_000.0,
            'T2': 10_000.0,
        }


def test_use_case_divergence_infra_route_lengths(use_case_divergence):
    assert use_case_divergence.route_lengths == \
        {
            'rt.D0->buffer_stop.2': 10_180.,
            'rt.D0->buffer_stop.1': 10_180.,
            'rt.buffer_stop.0->D0': 9_820.,
            'rt.D1->buffer_stop.0': 9_820.,
            'rt.buffer_stop.1->D1': 9_820.,
            'rt.D2->buffer_stop.0': 9_820.,
            'rt.buffer_stop.2->D2': 9_820.,
        }


def test_use_case_divergence_infra_num_switches(use_case_divergence):
    assert use_case_divergence.num_switches == 1


def test_use_case_divergence_infra_draw_infra_not_fail(use_case_divergence):
    """Test if it does not raise an exception"""
    try:
        use_case_divergence.draw_infra()
    except:  # noqa
        assert False


def test_use_case_divergence_infra_points_of_interest(use_case_divergence):
    poi = use_case_divergence.points_of_interest
    assert set(poi.keys()) == {'DVG'}


def test_use_case_divergence_infra_station_capacities(use_case_divergence):
    assert (
        use_case_divergence.station_capacities == {}
    )


def test_use_case_divergence_infra_num_stations(use_case_divergence):
    assert use_case_divergence.num_stations == 0


def test_use_case_divergence_points_on_tracks(use_case_divergence):
    expected = {
        'T0': {
            'S0': (9800.0, 'signal'),
            'D0': (9820.0, 'detector'),
            'DVG': (10000.0, 'switch', 'point')
        },
        'T1': {
            'DVG': (0, 'switch', 'point'),
            'D1': (180.0, 'detector'),
            'S1': (200.0, 'signal'),
        },
        'T2': {
            'DVG': (0, 'switch', 'point'),
            'D2': (180.0, 'detector'),
            'S2': (200.0, 'signal'),
        }
    }

    assert use_case_divergence.points_on_track_sections == expected


def test_use_case_divergence_route_tvds(use_case_divergence):
    expected = {
        'rt.D0->buffer_stop.2': 'DVG',
        'rt.D0->buffer_stop.1': 'DVG',
        'rt.buffer_stop.0->D0': 'D0<->buffer_stop.0',
        'rt.D1->buffer_stop.0': 'DVG',
        'rt.buffer_stop.1->D1': 'D1<->buffer_stop.1',
        'rt.D2->buffer_stop.0': 'DVG',
        'rt.buffer_stop.2->D2': 'D2<->buffer_stop.2'
    }

    assert use_case_divergence.route_tvds == expected


def test_use_case_divergence_simulation_type(use_case_divergence):
    assert isinstance(use_case_divergence.simulation, dict)


def test_use_case_divergence_simulation_num_trains(use_case_divergence):
    assert use_case_divergence.num_trains == 2


def test_use_case_divergence_simulation_trains(use_case_divergence):
    assert use_case_divergence.trains == ['train0', 'train1']


def test_use_case_divergence_simulation_departure_times(use_case_divergence):
    assert use_case_divergence.departure_times == [0, 100]


def test_use_case_divergence_results_length(use_case_divergence):
    assert len(use_case_divergence.results) == use_case_divergence.num_trains


def test_use_case_divergence_results_train_track_sections(use_case_divergence):
    assert use_case_divergence.train_track_sections(0) == {
        'T0': 'START_TO_STOP',
        'T1': 'START_TO_STOP',
    }
    assert use_case_divergence.train_track_sections(1) == {
        'T2': 'STOP_TO_START',
        'T0': 'STOP_TO_START',
    }


def test_use_case_divergence_points_encountered_by_train0(use_case_divergence):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in use_case_divergence.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'DEPARTURE', 'type': 'departure', 'offset': 50.0, },
        {'id': 'S0', 'type': 'signal', 'offset': 9800.0, },
        {'id': 'D0', 'type': 'detector', 'offset': 9820.0, },
        {'id': 'DVG', 'type': 'switch', 'offset': 10000.0, },
        {'id': 'D1', 'type': 'detector', 'offset': 10180.0, },
        {'id': 'S1', 'type': 'signal', 'offset': 10200.0, },
        {'id': 'ARRIVAL', 'type': 'arrival', 'offset': 19900.0, },
    ]
    assert points == expected


def test_use_case_divergence_points_encountered_by_train1_reverse(
    use_case_divergence
):
    points = [
        {
            k: v for k, v in d.items()
            if k not in ['t', 't_min']
        }
        for d in use_case_divergence.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'DEPARTURE', 'type': 'departure', 'offset': 50.0, },
        {'id': 'S2', 'type': 'signal', 'offset': 9800.0, },
        {'id': 'D2', 'type': 'detector', 'offset': 9820.0, },
        {'id': 'DVG', 'type': 'switch', 'offset': 10000.0, },
        {'id': 'D0', 'type': 'detector', 'offset': 10180.0, },
        {'id': 'S0', 'type': 'signal', 'offset': 10200.0, },
        {'id': 'ARRIVAL', 'type': 'arrival', 'offset': 19900.0, },
    ]
    assert points == expected


def test_use_case_divergence_space_time_graph(use_case_divergence):

    ax = use_case_divergence.space_time_graph(0, types_to_show=['switch'])

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 50.
    assert round(ax.dataLim.ymax) == 19_950.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['DVG', ]
    )
    assert ax.get_title() == "train0 (eco)"
    plt.close()
