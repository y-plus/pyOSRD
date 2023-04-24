from railjson_generator import (
    InfraBuilder,
    # SimulationBuilder,
    # Location,
)
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.infra.infra import Infra


def infra_cvg_dvg() -> Infra:
    """
    (T0)--S0-D0-                              -S4-D4-(T4)-->
                |                            |
            (CVG)>-(T2)-S2-D2----S3-D3-(T3)-<(DVG)
                |                            |
    (T1)--S1-D1-                              -S5-D5-(T5)-->

    """
    builder = InfraBuilder()
    T = [
        builder.add_track_section(label='T'+str(id), length=500)
        for id in range(6)
    ]
    builder.add_link(T[2].end(), T[3].begin())
    builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='CVG',
    )
    builder.add_point_switch(
        T[3].end(),
        T[4].begin(),
        T[5].begin(),
        label='DVG',
    )
    D = [
        T[i].add_detector(label='D'+str(i), position=450)
        if i in [0, 1, 3]
        else T[i].add_detector(label='D'+str(i), position=50)
        for i in range(6)
    ]
    S = [
        T[i].add_signal(D[i].position-20, Direction.START_TO_STOP, D[i])
        for i, _ in enumerate(D)
    ]
    for signal in S:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})

    infra = builder.build()

    return infra
