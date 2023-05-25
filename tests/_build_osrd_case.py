from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.infra.infra import Infra


def infra_cvg_dvg() -> Infra:
    """
    station0 (2 tracks)                        station1 (2 tracks)

    (T0)--S0-D0-                               -S4-D4-(T4)-->
                |                             |
            (CVG)>-(T2)-S2-D2--o--S3-D3-(T3)-<(DVG)
                |                             |
    (T1)--S1-D1-                               -S5-D5-(T5)-->

    All tracks are 500m long

    """
    infra_builder = InfraBuilder()
    T = [
        infra_builder.add_track_section(label='T'+str(id), length=500)
        for id in range(6)
    ]
    infra_builder.add_link(T[2].end(), T[3].begin())
    infra_builder.add_point_switch(
        T[2].begin(),
        T[0].end(),
        T[1].end(),
        label='CVG',
    )
    infra_builder.add_point_switch(
        T[3].end(),
        T[4].begin(),
        T[5].begin(),
        label='DVG',
    )
    D = [
        T[i].add_detector(label=f"D{i}", position=450)
        if i in [0, 1, 3]
        else T[i].add_detector(label=f"D{i}", position=50)
        for i in range(6)
    ]
    S = [
        T[i].add_signal(
            D[i].position-20,
            Direction.START_TO_STOP,
            D[i],
            label=f"S{i}"
        )
        for i, _ in enumerate(D)
    ]
    for signal in S:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})
    stations = [
        infra_builder.add_operational_point(label='station'+str(i))
        for i in range(2)
    ]
    for track in range(2):
        stations[0].add_part(T[track], 300)
    for track in range(4, 6):
        stations[1].add_part(T[track], 300)

    infra = infra_builder.build()

    return infra


def simulation_cvg_dvg_two_trains(built_infra: Infra):

    sim_builder = SimulationBuilder(built_infra)

    for train_id in range(2):
        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[train_id], 300),
            Location(built_infra.track_sections[train_id+4], 300),
            label='train'+str(train_id),
            departure_time=train_id*100.
        )
    built_simulation = sim_builder.build()
    return built_simulation
