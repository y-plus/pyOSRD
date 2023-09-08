"""
use_case_straight_line

station A (1 track)                        station B (1 track)

            ┎SA                                    SB┐
    (T)-|----DA------------------------------------DB-----|---->

10 km long
Train #1 start from A and arrive at B
Train #2 start from B and arrive at A
The two train collide !
"""  # noqa


import matplotlib.pyplot as plt
from plotly import graph_objects as go

from rlway.pyosrd.osrd import Point


def test_straight_line_infra(use_case_straight_line):
    assert isinstance(use_case_straight_line.infra, dict)


def test_straight_line_infra_routes(use_case_straight_line):
    assert set(use_case_straight_line.routes) == \
        set([
            'rt.buffer_stop.0->DA',
            'rt.DA->buffer_stop.1',
            'rt.DB->buffer_stop.0',
            'rt.buffer_stop.1->DB'
        ])


def test_straight_line_infra_block_lengths(use_case_straight_line):
    assert use_case_straight_line.track_section_lengths == \
        {
            'T': 10_000.0,
        }


def test_straight_line_infra_num_switches(use_case_straight_line):
    assert use_case_straight_line.num_switches == 0


def test_straight_line_infra_draw_infra_not_fail(
    use_case_straight_line
):
    """Test if it does not raise an exception"""
    try:
        use_case_straight_line.draw_infra()
    except:  # noqa
        assert False


def test_straight_line_infra_station_capacities(
    use_case_straight_line
):
    assert (
        use_case_straight_line.station_capacities == {
            'stationA': 1,
            'stationB': 1,
        }
    )


def test_straight_line_infra_num_stations(use_case_straight_line):
    assert use_case_straight_line.num_stations == 2


def test_straight_line_points_on_tracks(use_case_straight_line):
    expected = {
        "T": [
            Point(id='buffer_stop.0', track_section='T', position=0.0, type='buffer_stop'),  # noqa
            Point(id='stationA', track_section='T', position=460, type='station'),  # noqa
            Point(id='SA', track_section='T', position=480, type="signal"),  # noqa
            Point(id='DA', track_section='T', position=500, type="detector"),  # noqa
            Point(id='DB', track_section='T', position=9_500, type="detector"),  # noqa
            Point(id='SB', track_section='T', position=9_520, type="signal"),  # noqa
            Point(id='stationB', track_section='T', position=9_540, type='station'),  # noqa
            Point(id='buffer_stop.1', track_section='T', position=10_000, type='buffer_stop'),  # noqa
        ],
    }

    assert use_case_straight_line.points_on_track_sections == expected


def test_straight_line_simulation_type(use_case_straight_line):
    assert isinstance(use_case_straight_line.simulation, dict)


def test_straight_line_simulation_num_trains(use_case_straight_line):
    assert use_case_straight_line.num_trains == 2


def test_straight_line_simulation_trains(use_case_straight_line):
    assert use_case_straight_line.trains == ['train0', 'train1']


def test_straight_line_simulation_departure_times(
    use_case_straight_line
):
    assert use_case_straight_line.departure_times == [0, 420.]


def test_straight_line_results_length(use_case_straight_line):
    num_trains = use_case_straight_line.num_trains
    assert len(use_case_straight_line.results) == num_trains


def test_straight_line_results_train_track_sections(
    use_case_straight_line
):
    tracks_0 = [
        {'id': 'T', 'direction': 'START_TO_STOP'}
    ]
    assert use_case_straight_line.train_track_sections(0) == tracks_0
    tracks_1 = [
        {'id': 'T', 'direction': 'STOP_TO_START'}
    ]
    assert use_case_straight_line.train_track_sections(1) == tracks_1


def test_straight_line_results_points_encountered_by_train(
    use_case_straight_line
):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in use_case_straight_line.points_encountered_by_train(0)
    ]
    expected = [
        {'id': 'departure_train0', 'offset': 0.0, 'type': 'departure'},
        {'id': 'stationA', 'offset': 0.0, 'type': 'station'},
        {'id': 'SA', 'offset': 20.0, 'type': 'signal'},
        {'id': 'DA', 'offset': 40.0, 'type': 'detector'},
        {'id': 'DB', 'offset': 9_040.0, 'type': 'detector'},
        {'id': 'stationB', 'offset': 9_080.0, 'type': 'station'},
        {'id': 'arrival_train0', 'offset': 9_080.0, 'type': 'arrival'},
    ]
    assert expected == points


def test_straight_line_results_points_encountered_by_train_revert(
    use_case_straight_line
):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in use_case_straight_line.points_encountered_by_train(1)
    ]
    expected = [
        {'id': 'departure_train1', 'offset': 0.0, 'type': 'departure'},
        {'id': 'stationB', 'offset': 0.0, 'type': 'station'},
        {'id': 'SB', 'offset': 20.0, 'type': 'signal'},
        {'id': 'DB', 'offset': 40.0, 'type': 'detector'},
        {'id': 'DA', 'offset': 9_040.0, 'type': 'detector'},
        {'id': 'stationA', 'offset': 9_080.0, 'type': 'station'},
        {'id': 'arrival_train1', 'offset': 9_080.0, 'type': 'arrival'},
    ]
    assert expected == points


def test_straight_line_space_time_chart(use_case_straight_line):

    ax = use_case_straight_line.space_time_chart(
        0,
        points_to_show=['station']
    )

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == 9_080.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['stationA', 'stationB']
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()


def test_straight_line_space_time_chart_plotly(use_case_straight_line):

    for train, _ in enumerate(use_case_straight_line.trains):
        fig = use_case_straight_line.space_time_chart_plotly(train)
        assert isinstance(fig, go.Figure)


def test_straight_line_tvd_blocks(use_case_straight_line):

    expected = {
        'DA<->buffer_stop.0': 'DA<->buffer_stop.0',
        'DA<->DB': 'DA<->DB',
        'DB<->buffer_stop.1': 'DB<->buffer_stop.1'
    }
    assert use_case_straight_line.tvd_blocks == expected


def test_straight_line_entry_signals(use_case_straight_line):

    expected = [
        {
            'DA<->buffer_stop.0': None,
            'DA<->DB': 'SA',
            'DB<->buffer_stop.1': 'SA',
        },
        {
            'DB<->buffer_stop.1': None,
            'DA<->DB': 'SB',
            'DA<->buffer_stop.0': 'SB',
        },
    ]
    assert use_case_straight_line.entry_signals == expected
