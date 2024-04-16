import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from pyosrd.infra.helpers.station_builder import build_N_dvg_station_cvg


def station_builder_1station_2trains(
    dir: str,
    infra_json: str = 'infra.json',
    simulation_json: str = 'simulation.json'
) -> None:
    """Generate a divergence/stations/convergence sequence.

                                        stations

                                     ┎S1           S2┐
                                ------D1---(t1)----D2--
                              /                        \
        ----(track_in)---D0--<DVG                    CVG>-D5-----(track_out)-
                              \     ┎S3           S4┐  /
                                -----D3----(t2)---D4---

    """  # noqa
    infra_builder = InfraBuilder()

    t0 = infra_builder.add_track_section(label="T0", length=1000)

    t0 = build_N_dvg_station_cvg(
        infra_builder,
        t0,
        "station_builder_1station",
        1
    )

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    sim_builder = SimulationBuilder()

    for i in range(0, 2):
        sim_builder.add_train_schedule(
            Location(built_infra.track_sections[0], 500),
            Location(built_infra.track_sections[1], 500),
            label='train'+str(i),
            departure_time=i*200.+0.,
        )

    built_simulation = sim_builder.build()
    built_simulation.save(os.path.join(dir, simulation_json))
