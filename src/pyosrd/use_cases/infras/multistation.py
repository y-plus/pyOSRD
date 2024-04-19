import os

from importlib.resources import files

from railjson_generator import (
    InfraBuilder,
)

from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.simulation.simulation import (
    register_rolling_stocks
)

from pyosrd.infra.helpers.station_builder import build_N_dvg_station_cvg

register_rolling_stocks(files('pyosrd').joinpath('rolling_stocks'))


def multistation(
    dir: str,
    infra_json: str = 'infra.json',
    num_stations: int = 1
) -> Infra:
    """Create a serie of N stations (see build_N_dvg_station_cvg for details).

    Generate a divergence/stations/convergence sequence.

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
    t0.add_buffer_stop(0, label='buffer_stop.0')

    t0 = build_N_dvg_station_cvg(
        infra_builder,
        t0,
        "multistation",
        num_stations
    )

    t0.add_buffer_stop(1000, label='buffer_stop.1')

    os.makedirs(dir, exist_ok=True)

    built_infra = infra_builder.build()
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra
