import os

from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction


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
        infra_builder.add_track_section(label="T"+str(id), track_name="T"+str(id), length=500)
        for id in range(3)
    ]
    T[0].add_buffer_stop(0, label="buffer_stop.0")

    for i in [1, 2]:
        T[i].add_buffer_stop(T[i].length, label=f"buffer_stop.{i}")

    dvg = infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label="DVG",
    )

    DVG_COORDS = (0.21, 45.575988410701974)
    PINCH = 0.75
    dvg.set_coords(*DVG_COORDS)

    t0_begin = inverse_haversine(DVG_COORDS[::-1], 250, direction=Dir.WEST, unit='m')[::-1]
    T[0].set_remaining_coords([t0_begin])


    t1_mid = inverse_haversine(DVG_COORDS[::-1], 250, direction=Dir.NORTHEAST+PINCH, unit='m')[::-1]
    t1_end = inverse_haversine(t1_mid[::-1], 250, direction=Dir.EAST, unit='m')[::-1]
    T[1].set_remaining_coords([t1_mid, t1_end])
    t2_mid = inverse_haversine(DVG_COORDS[::-1], 250, direction=Dir.SOUTHEAST-PINCH, unit='m')[::-1]
    t2_end = inverse_haversine(t2_mid[::-1], 250, direction=Dir.EAST, unit='m')[::-1]
    T[2].set_remaining_coords([t2_mid, t2_end])

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
