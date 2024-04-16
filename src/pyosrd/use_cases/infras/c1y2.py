import os

from importlib.resources import files

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.simulation.simulation import (
    register_rolling_stocks
)

register_rolling_stocks(files('pyosrd').joinpath('rolling_stocks'))


def c1y2(
    dir: str,
    infra_json: str = 'infra.json'
) -> Infra:
    """
                         S1┐
                        -D1---------(T1)-->
                ┎S0   /
    --(T0)--------D0-<(DVG)
                      \  S2┐
                        -D2----------(T2)-->

    All tracks are 500 m long
    """  # noqa

    infra_builder = InfraBuilder()

    T = [
        infra_builder.add_track_section(label="T"+str(id), length=500)
        for id in range(3)
    ]
    T[0].add_buffer_stop(0, label="buffer_stop.0")

    for i in [1, 2]:
        T[i].add_buffer_stop(T[i].length, label=f"buffer_stop.{i}")

    infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label="DVG",
    )
    detectors = [T[0].add_detector(label="D0", position=T[0].length-50)]
    detectors += [
        T[i].add_detector(
            label=f"D{i}",
            position=50,
        )
        for i in [1, 2]
    ]
    signals = [
        T[0].add_signal(
            detectors[0].position-20,
            Direction.START_TO_STOP,
            is_route_delimiter=True,
            label="S0"
        ),
    ]
    signals += [
        T[i].add_signal(
            detectors[i].position+20,
            Direction.STOP_TO_START,
            is_route_delimiter=True,
            label=f"S{i}"
        )
        for i in [1, 2]
    ]

    for signal in signals:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    for i, track in enumerate(T):
        infra_builder.add_operational_point(label=f"station{i}").add_part(
            track=track,
            offset=(
                10 if i == 0 else track.length - 10
            )
        )

    built_infra = infra_builder.build()

    os.makedirs(dir, exist_ok=True)
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
