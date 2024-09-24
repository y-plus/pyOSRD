import os


from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra

from pyosrd.infra.helpers.station_builder import build_N_dvg_station_cvg


def multistation(
    dir: str,
    infra_json: str = 'infra.json',
    num_stations: int = 1
) -> Infra:
    """Create a serie of N stations (see build_N_dvg_station_cvg for details).

    Generate a divergence/stations/convergence sequence.

                                        stations

                                     S1┐         ┎S2
                                -----D1---(t1)----D2--
                        ┎S0   /                        \  S5┐
        ----(track_in)---D0--<DVG                    CVG>-D5-----(track_out)-
                              \      S3┐         ┎S4  /
                                -----D3----(t2)---D4--


    """  # noqa
    infra_builder = InfraBuilder()

    t0 = infra_builder.add_track_section(label="T0", length=1000)
    t0.add_buffer_stop(0, label='buffer_stop.0')
    
    begin = (45.575988410701974, 0.21)
    t0.set_remaining_coords([begin[::-1]])

    t0 = build_N_dvg_station_cvg(
        infra_builder,
        t0,
        "multistation",
        num_stations
    )
    
    t0.add_buffer_stop(1000, label='buffer_stop.1')
    
    first_track = next(
        t 
        for t in infra_builder.infra.track_sections
        if t.label=='T0'
    )

    first_track.set_remaining_coords(
        [begin[::-1]]
    )
    first_track.coordinates = first_track.coordinates[::-1]

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
