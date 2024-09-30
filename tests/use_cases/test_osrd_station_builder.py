"""
osrd_station_builder
"""
import matplotlib.pyplot as plt

from pyosrd.osrd import Point


def test_station_builder_infra(simulation_station_builder):
    assert isinstance(simulation_station_builder.infra, dict)


def test_station_builder_infra_routes(simulation_station_builder):
    assert set(simulation_station_builder.routes) == \
        set([
            'rt.buffer_stop.0->station_builder_1station.0.D0',
            'rt.station_builder_1station.0.D0->station_builder_1station.0.D2',
            'rt.station_builder_1station.0.D0->station_builder_1station.0.D4',
            'rt.station_builder_1station.0.D1->buffer_stop.0',
            'rt.station_builder_1station.0.D2->buffer_stop.1',
            'rt.station_builder_1station.0.D3->buffer_stop.0',
            'rt.station_builder_1station.0.D4->buffer_stop.1',
            'rt.buffer_stop.1->station_builder_1station.0.D5',
            'rt.station_builder_1station.0.D5->station_builder_1station.0.D1',
            'rt.station_builder_1station.0.D5->station_builder_1station.0.D3',
        ])


def test_station_builder_infra_block_lengths(simulation_station_builder):
    assert simulation_station_builder.track_section_lengths == \
        {
            'T0': 1000.0,
            'station_builder_1station.0.T1': 1000.0,
            'station_builder_1station.0.T2': 1000.0,
            'station_builder_1station.0.Tout': 1000.0
        }


def test_station_builder_infra_num_switches(simulation_station_builder):
    assert simulation_station_builder.num_switches == 2


def test_station_builder_infra_draw_infra_not_fail(simulation_station_builder):
    """Test if it does not raise an exception"""
    try:
        simulation_station_builder.draw_infra_points()
    except:  # noqa
        assert False


def test_station_builder_infra_station_capacities(simulation_station_builder):
    assert (
        simulation_station_builder.station_capacities
        == {'station_builder_1station.0.s': 2}
    )


def test_station_builder_infra_num_stations(simulation_station_builder):
    assert simulation_station_builder.num_stations == 1


def test_station_builder_points_on_tracks(simulation_station_builder):
    expected = {
        'T0':[
            Point(track_section='T0', position=0.0, id='buffer_stop.0', type='buffer_stop'),
            Point(track_section='T0', position=960.0, id='station_builder_1station.0.S0', type='signal'),
            Point(track_section='T0', position=980.0, id='station_builder_1station.0.D0', type='detector'),
            Point(track_section='T0', position=1000.0, id='station_builder_1station.0.DVG', type='switch')
        ],
        'station_builder_1station.0.T1':[
            Point(track_section='station_builder_1station.0.T1', position=0, id='station_builder_1station.0.DVG', type='switch'),
            Point(track_section='station_builder_1station.0.T1', position=200.0, id='station_builder_1station.0.D1', type='detector'),
            Point(track_section='station_builder_1station.0.T1', position=220.0, id='station_builder_1station.0.S1', type='signal'),
            Point(track_section='station_builder_1station.0.T1', position=500.0, id='station_builder_1station.0.s/V1', type='station'),
            Point(track_section='station_builder_1station.0.T1', position=800.0, id='station_builder_1station.0.S2', type='signal'),
            Point(track_section='station_builder_1station.0.T1', position=820.0, id='station_builder_1station.0.D2', type='detector'),
            Point(track_section='station_builder_1station.0.T1', position=1000.0, id='station_builder_1station.0.CVG', type='switch')
        ],
        'station_builder_1station.0.T2':[
            Point(track_section='station_builder_1station.0.T2', position=0, id='station_builder_1station.0.DVG', type='switch'),
            Point(track_section='station_builder_1station.0.T2', position=200.0, id='station_builder_1station.0.D3', type='detector'),
            Point(track_section='station_builder_1station.0.T2', position=220.0, id='station_builder_1station.0.S3', type='signal'),
            Point(track_section='station_builder_1station.0.T2', position=500.0, id='station_builder_1station.0.s/V2', type='station'),
            Point(track_section='station_builder_1station.0.T2', position=800.0, id='station_builder_1station.0.S4', type='signal'),
            Point(track_section='station_builder_1station.0.T2', position=820.0, id='station_builder_1station.0.D4', type='detector'),
            Point(track_section='station_builder_1station.0.T2', position=1000.0, id='station_builder_1station.0.CVG', type='switch')
        ],
        'station_builder_1station.0.Tout':[
            Point(track_section='station_builder_1station.0.Tout', position=0, id='station_builder_1station.0.CVG', type='switch'),
            Point(track_section='station_builder_1station.0.Tout', position=20.0, id='station_builder_1station.0.D5', type='detector'),
            Point(track_section='station_builder_1station.0.Tout', position=40.0, id='station_builder_1station.0.S5', type='signal'),
            Point(track_section='station_builder_1station.0.Tout', position=1000.0, id='buffer_stop.1', type='buffer_stop')]
        }

    assert simulation_station_builder.points_on_track_sections() == expected


def test_station_builder_simulation_type(simulation_station_builder):
    assert isinstance(simulation_station_builder.simulation, dict)


def test_station_builder_simulation_num_trains(simulation_station_builder):
    assert simulation_station_builder.num_trains == 2


def test_station_builder_simulation_trains(simulation_station_builder):
    assert simulation_station_builder.trains == ['train0', 'train1']


def test_station_builder_simulation_departure_times(
    simulation_station_builder
):
    assert simulation_station_builder.departure_times == [0, 200]


def test_station_builder_has_results(simulation_station_builder):
    assert simulation_station_builder.has_results


def test_station_builder_results_length(simulation_station_builder):
    assert (
        len(simulation_station_builder.results)
        == simulation_station_builder.num_trains
    )


def test_station_builder_results_train_track_sections(
    simulation_station_builder
):
    assert simulation_station_builder.train_track_sections(0) == [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'station_builder_1station.0.T1', 'direction': 'START_TO_STOP'},
    ]
    assert simulation_station_builder.train_track_sections(1) == [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'station_builder_1station.0.T1', 'direction': 'START_TO_STOP'},
    ]


def test_station_builder_results_pts_encountered_by_train(
    simulation_station_builder
):
    points = [
        {
            k: v for k, v in d.items()
            if not k.startswith('t_')
        }
        for d in simulation_station_builder.points_encountered_by_train(0)
    ]
    expected = [
        {
            'id': 'departure_train0',
            'offset': 0.0,
            'type': 'departure',
        },
        {
            'id': 'station_builder_1station.0.S0',
            'offset': 460.0,
            'type': 'signal',
        },
        {
            'id': 'station_builder_1station.0.D0',
            'offset': 480.0,
            'type': 'detector',
        },
        {
            'id': 'station_builder_1station.0.DVG',
            'offset': 500.0,
            'type': 'switch',
        },
        {
            'id': 'station_builder_1station.0.D1',
            'offset': 700.0,
            'type': 'detector',
        },
        {
            'id': 'station_builder_1station.0.s/V1',
            'offset': 1000.0,
            'type': 'station',
        },
        {
            'id': 'arrival_train0',
            'offset': 1000.0,
            'type': 'arrival',
        }
  ]
    assert points == expected


def test_station_builder_space_time_chart(simulation_station_builder):

    ax = simulation_station_builder.space_time_chart(
        0,
        points_to_show=['station']
    )

    assert ax.dataLim.xmin == 0.
    assert round(ax.dataLim.ymin) == 0.
    assert round(ax.dataLim.ymax) == 1000.
    assert (
        [label._text for label in ax.get_yticklabels()]
        == ['station_builder_1station.0.s/V1']
    )
    assert ax.get_title() == "train0 (base)"
    plt.close()


def test_station_builder_tvd_zones(simulation_station_builder):

    expected = {
        'buffer_stop.0<->station_builder_1station.0.D0': 'buffer_stop.0<->station_builder_1station.0.D0',  # noqa
        'station_builder_1station.0.D0<->station_builder_1station.0.D3': 'station_builder_1station.0.DVG',  # noqa
        'station_builder_1station.0.D0<->station_builder_1station.0.D1': 'station_builder_1station.0.DVG',  # noqa
        'station_builder_1station.0.D1<->station_builder_1station.0.D2': 'station_builder_1station.0.D1<->station_builder_1station.0.D2',  # noqa
        'station_builder_1station.0.D2<->station_builder_1station.0.D5': 'station_builder_1station.0.CVG',  # noqa
        'buffer_stop.1<->station_builder_1station.0.D5': 'buffer_stop.1<->station_builder_1station.0.D5',  # noqa
        'station_builder_1station.0.D3<->station_builder_1station.0.D4': 'station_builder_1station.0.D3<->station_builder_1station.0.D4',  # noqa
        'station_builder_1station.0.D4<->station_builder_1station.0.D5': 'station_builder_1station.0.CVG'  # noqa
    }
    assert simulation_station_builder.tvd_zones == expected


def test_station_builder_stop_positions(simulation_station_builder):

    expected =[
        {
            'buffer_stop.0<->station_builder_1station.0.D0': {
                'type': 'signal',
                'offset': 460.0,
                'id': 'station_builder_1station.0.D2'
            },
            'station_builder_1station.0.DVG': {
                'type': 'switch',
                'offset': None
            },
            'station_builder_1station.0.D1<->station_builder_1station.0.D2': {
                'type': 'last_zone',
                'offset': None
            },
        },
        {
            'buffer_stop.0<->station_builder_1station.0.D0': {
                'type': 'signal',
                'offset': 460.0,
                'id': 'station_builder_1station.0.D2'
            },
            'station_builder_1station.0.DVG': {
                'type': 'switch',
                'offset': None
            },
            'station_builder_1station.0.D1<->station_builder_1station.0.D2': {
                'type': 'last_zone',
                'offset': None
            }
        }
    ]

    for k in simulation_station_builder.stop_positions[0]:
        assert simulation_station_builder.stop_positions[0][k] == expected[0][k]


def test_station_builder_path_length(simulation_station_builder):

    assert simulation_station_builder.path_length(0) == 1_000
    assert simulation_station_builder.path_length(1) == 1_000


def test_station_builder_train_routes(simulation_station_builder):

    assert simulation_station_builder.train_routes(0) ==\
        [
            'rt.buffer_stop.0->station_builder_1station.0.D0',
            'rt.station_builder_1station.0.D0->station_builder_1station.0.D2',
        ]


def test_station_builder_route_track_sections(simulation_station_builder):

    assert simulation_station_builder.route_track_sections(
        'rt.station_builder_1station.0.D0->station_builder_1station.0.D4'
    ) == [
        {'id': 'T0', 'direction': 'START_TO_STOP'},
        {'id': 'station_builder_1station.0.T2', 'direction': 'START_TO_STOP'}
    ]
