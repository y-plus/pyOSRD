from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.infra.infra import Infra


def infra_two_lanes() -> Infra:
    """
    osrd_two_lanes
    --------------
                        station (2 tracks)

                          --------S1-D1-(T1)
                        /                    \
    --(T0)-------S0-D0-<(DVG)            (CVG)>-----------(T3)--->
                        \                    /
                          --------S2-D2-(T2)

    All tracks are 1 km long
    Train 0 starts from T0 at t=0s, stops at T1, and arrives at T3
    Train 1 starts from T at t=60s, stops at T2, and arrives at T3
    """  # noqa

    infra_builder = InfraBuilder()
    T = [
        infra_builder.add_track_section(label='T'+str(id), length=1000)
        for id in range(4)
    ]
    infra_builder.add_point_switch(
        T[3].begin(),
        T[1].end(),
        T[2].end(),
        label='CVG',
    )
    infra_builder.add_point_switch(
        T[0].end(),
        T[1].begin(),
        T[2].begin(),
        label='DVG',
    )
    detectors = [
        track_section.add_detector(
            label=f"D{i}",
            position=T[i].length-180,
        )
        for i, track_section in enumerate(T)
    ]
    signals = [
        track_section.add_signal(
            detectors[i].position-20,
            Direction.START_TO_STOP,
            detectors[i],
            label=f"S{i}"
        )
        for i, track_section in enumerate(T)
    ]
    for signal in signals:
        signal.add_logical_signal("BAL", settings={"Nf": "true"})
    station = infra_builder.add_operational_point(label='station')
    for i in [1, 2]:
        station.add_part(T[i], signals[i].position-10)

    infra = infra_builder.build()

    return infra


def simulation_two_lanes_two_trains(built_infra: Infra):

    sim_builder = SimulationBuilder(built_infra)

    for i in range(2):
        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[0], (i+1)*100.),
            Location(built_infra.track_sections[i+1], 790),
            Location(built_infra.track_sections[3], 980),
            label='train'+str(i),
            departure_time=i*60.,
        )
    built_simulation = sim_builder.build()
    return built_simulation
