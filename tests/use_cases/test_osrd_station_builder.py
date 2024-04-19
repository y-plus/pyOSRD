"""
osrd_station_builder
---------
station0 (2 tracks)                        station1 (2 tracks)

        ┎S0                                      S4┐
(T0)-----D0-                                  --D4---------(T4)-->
              \   S2┐                   ┎S3  /
            CVG>-D2-----(T2)--+--(T3)----D3-<DVG
        ┎S1   /                              \   S5┐
(T1)-----D1-                                  --D5---------(T5)-->

All tracks are 500m long
Train 0 starts from T0 at t=0 and arrives at T4
Train 1 starts from T1 at t=100 and arrives at T5
"""  # noqa

import matplotlib.pyplot as plt

from pyosrd.osrd import Point


def test_station_builder_infra(simulation_station_builder):
    assert isinstance(simulation_station_builder.infra, dict)


def test_station_builder_infra_routes(simulation_station_builder):
    assert set(simulation_station_builder.routes) == \
        set([
            'rt.station_builder_1station.0.D4->buffer_stop.0',
            'rt.buffer_stop.0->station_builder_1station.0.D1',
            'rt.station_builder_1station.0.D2->buffer_stop.0',
            'rt.buffer_stop.1->station_builder_1station.0.D2',
            'rt.buffer_stop.1->station_builder_1station.0.D4',
            'rt.buffer_stop.0->station_builder_1station.0.D3',
            'rt.station_builder_1station.0.D3->buffer_stop.1',
            'rt.station_builder_1station.0.D1->buffer_stop.1'
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
        "T0": [
            Point(track_section="T0", position=0.0, id="buffer_stop.0", type="buffer_stop"),  # noqa
            Point(track_section="T0", position=980.0, id="station_builder_1station.0.D0", type="detector"),  # noqa
            Point(track_section="T0", position=1000.0, id="station_builder_1station.0.DVG", type="switch"),  # noqa
        ],
        "station_builder_1station.0.T1": [
            Point(track_section="station_builder_1station.0.T1", position=0, id="station_builder_1station.0.DVG", type="switch"),  # noqa
            Point(track_section="station_builder_1station.0.T1", position=380.0, id="station_builder_1station.0.S1", type="signal"),  # noqa
            Point(track_section="station_builder_1station.0.T1", position=400.0, id="station_builder_1station.0.D1", type="detector"),  # noqa
            Point(track_section="station_builder_1station.0.T1", position=500.0, id="station_builder_1station.0.s", type="station"),  # noqa
            Point(track_section="station_builder_1station.0.T1", position=800.0, id="station_builder_1station.0.D2", type="detector"),  # noqa
            Point(track_section="station_builder_1station.0.T1", position=820.0, id="station_builder_1station.0.S2", type="signal"),  # noqa
            Point(track_section="station_builder_1station.0.T1", position=1000.0, id="station_builder_1station.0.CVG", type="switch"),  # noqa
        ],
        "station_builder_1station.0.T2": [
            Point(track_section="station_builder_1station.0.T2", position=0, id="station_builder_1station.0.DVG", type="switch"),  # noqa
            Point(track_section="station_builder_1station.0.T2", position=380.0, id="station_builder_1station.0.S3", type="signal"),  # noqa
            Point(track_section="station_builder_1station.0.T2", position=400.0, id="station_builder_1station.0.D3", type="detector"),  # noqa
            Point(track_section="station_builder_1station.0.T2", position=500.0, id="station_builder_1station.0.s", type="station"),  # noqa
            Point(track_section="station_builder_1station.0.T2", position=800.0, id="station_builder_1station.0.D4", type="detector"),  # noqa
            Point(track_section="station_builder_1station.0.T2", position=820.0, id="station_builder_1station.0.S4", type="signal"),  # noqa
            Point(track_section="station_builder_1station.0.T2", position=1000.0, id="station_builder_1station.0.CVG", type="switch"),  # noqa
        ],
        "station_builder_1station.0.Tout": [
            Point(track_section="station_builder_1station.0.Tout", position=0, id="station_builder_1station.0.CVG", type="switch"),  # noqa
            Point(track_section="station_builder_1station.0.Tout", position=20.0, id="station_builder_1station.0.D5", type="detector"),  # noqa
            Point(track_section="station_builder_1station.0.Tout", position=1000.0, id="buffer_stop.1", type="buffer_stop"),  # noqa
        ],
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
        { "id": "departure_train0", "offset": 0.0, "type": "departure" },  # noqa
        { "id": "station_builder_1station.0.D0", "offset": 480.0, "type": "detector" },  # noqa
        { "id": "station_builder_1station.0.DVG", "offset": 500.0, "type": "switch" },  # noqa
        { "id": "station_builder_1station.0.S1", "offset": 880.0, "type": "signal" },  # noqa
        { "id": "station_builder_1station.0.D1", "offset": 900.0, "type": "detector" },  # noqa
        { "id": "station_builder_1station.0.s", "offset": 1000.0, "type": "station" },  # noqa
        { "id": "arrival_train0", "offset": 1000.0, "type": "arrival" },  # noqa
        { "id": "station_builder_1station.0.D2", "offset": 1300.0, "type": "detector" },  # noqa,
        { "id": "station_builder_1station.0.CVG", "offset": 1500.0, "type": "switch" }  # noqa
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
        == ['station_builder_1station.0.s']
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

    expected = [
        {
            "buffer_stop.0<->station_builder_1station.0.D0": {
                "type": "station",
                "offset": 1000.0,
                "id": "station_builder_1station.0.s"
            },
            "station_builder_1station.0.DVG": {
                "type": "signal",
                "offset": 880.0,
                "id": "station_builder_1station.0.D0"
            },
            "station_builder_1station.0.D1<->station_builder_1station.0.D2": {
                "type": "signal",
                "offset": 1000.0,
                "id": "station_builder_1station.0.s"
            }
        },
        {
            "buffer_stop.0<->station_builder_1station.0.D0": {
                "type": "station",
                "offset": 1000.0,
                "id": "station_builder_1station.0.s"
            },
            "station_builder_1station.0.DVG": {
                "type": "signal",
                "offset": 880.0,
                "id": "station_builder_1station.0.D0"
            },
            "station_builder_1station.0.D1<->station_builder_1station.0.D2": {
                "type": "signal",
                "offset": 1000.0,
                "id": "station_builder_1station.0.s"
            }
        }
    ]

    assert simulation_station_builder.stop_positions == expected
