import rlway.osrd.infra as infr


def test_infra(infra_test):
    assert isinstance(infra_test, dict)


def test_infra_routes(infra_test):
    assert set(infr.routes(infra_test)) == \
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


def test_infra_route_switches(infra_test):
    assert infr.route_switches(infra_test) == \
        {
            'rt.D0->D2': 'CVG',
            'rt.D1->D2': 'CVG',
            'rt.D3->D5': 'DVG',
            'rt.D3->D4': 'DVG',
        }


def test_infra_route_limits(infra_test):
    assert infr.route_limits(infra_test) == \
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


def test_infra_track_section_lengths(infra_test):
    assert infr.track_section_lengths(infra_test) == \
        {
            'T0': 500.0,
            'T1': 500.0,
            'T2': 500.0,
            'T3': 500.0,
            'T4': 500.0,
            'T5': 500.0
        }


def test_infra_route_lengths(infra_test):
    assert infr.route_lengths(infra_test) == \
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


def test_infra_draw_infra_not_fail(infra_test):
    try:
        infr.draw_infra(infra_test)
    except:  # noqa
        assert False
