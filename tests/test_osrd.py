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
    assert osrd_case.departure_times == [0, 0]