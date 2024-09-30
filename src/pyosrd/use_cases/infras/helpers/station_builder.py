from haversine import inverse_haversine, Direction as Dir

from railjson_generator import (
    InfraBuilder
)
from railjson_generator.schema.infra.infra import TrackSection
from railjson_generator.schema.infra.direction import Direction


def build_dvg_station_cvg(
    infra_builder: InfraBuilder,
    track_in: TrackSection,
    name: str,
) -> TrackSection:
    """Generate a divergence/stations/convergence sequence.

                                        stations

                                     S1┐         ┎S2
                                -----D1---(t1)----D2--
                        ┎S0   /                        \  S5┐
        ----(track_in)---D0--<DVG                    CVG>-D5-----(track_out)-
                              \      S3┐         ┎S4  /
                                -----D3----(t2)---D4--


    Parameters
    ----------
    infra_builder : InfraBuilder
        The InfraBuilder to be used to create all sections, switches
        and any other necessary part of the infra.
    track_in : TrackSection
        The track section to be used to connect the start of the
        sub infra.
    name : str
        The name to be used to name all sections, switches in infra
        created.

    Returns
    -------
    TrackSection
        The track section going out of the the station created.
    """ # noqa


    t1 = infra_builder.add_track_section(
        label=name+".T1",
        length=1000,
        track_name="V1"
    )
    t2 = infra_builder.add_track_section(
        label=name+".T2",
        length=1000,
        track_name="V2"
    )
    track_out = infra_builder.add_track_section(
        label=name+".Tout",
        length=1000
    )

    dvg = infra_builder.add_point_switch(
        track_in.end(),
        t1.begin(),
        t2.begin(),
        label=name+'.DVG',
    )
    cvg = infra_builder.add_point_switch(
        track_out.begin(),
        t1.end(),
        t2.end(),
        label=name+'.CVG',
    )

    track_in_begin = track_in.coordinates[0][::-1]

    dvg_coords = inverse_haversine(
        track_in_begin,
        track_in.length,
        Dir.EAST,
        unit='m'
    )
    dvg.set_coords(*dvg_coords[::-1])

    t1_1_coords = inverse_haversine(
        dvg_coords,
        20,
        Dir.NORTHEAST,
        unit='m'
    )
    t1_2_coords = inverse_haversine(
        t1_1_coords,
        t1.length - 2 * 20.,
        Dir.EAST,
        unit='m'
    )
    cvg_coords = inverse_haversine(
        t1_2_coords,
        20.,
        Dir.SOUTHEAST,
        unit='m'
    )
    cvg.set_coords(*cvg_coords[::-1])
    t1.set_remaining_coords([t1_1_coords[::-1], t1_2_coords[::-1]])
    t2_1_coords = inverse_haversine(
            dvg_coords,
            20,
            Dir.SOUTHEAST,
            unit='m'
        )
    t2_2_coords = inverse_haversine(
            t2_1_coords,
            t2.length - 2 * 20.,
            Dir.EAST,
            unit='m'
    )
    t2.set_remaining_coords([t2_1_coords[::-1], t2_2_coords[::-1]])

    track_out_end = inverse_haversine(
        cvg_coords,
        track_out.length,
        Dir.EAST,
        unit='m'
    )
    track_out.set_remaining_coords([track_out_end[::-1]])
    
    # D0
    track_in.add_detector(
            label=name+'.D0',
            position=track_in.length - 20,
        )
    s = track_in.add_signal(
                    track_in.length - 40,
                    Direction.START_TO_STOP,
                    is_route_delimiter=True,
                    label=name+'.S0',
                )
    s.add_logical_signal("BAL", settings={"Nf": "true"})

    # D1/S1
    t1.add_detector(
            label=name+'.D1',
            position=200,
        )
    s = t1.add_signal(
                    220,
                    Direction.STOP_TO_START,
                    is_route_delimiter=True,
                    label=name+'.S1',
                )
    s.add_logical_signal("BAL", settings={"Nf": "true"})

    # D2/S2
    t1.add_detector(
            label=name+'.D2',
            position=820,
        )
    s = t1.add_signal(
                    800,
                    Direction.START_TO_STOP,
                    is_route_delimiter=True,
                    label=name+'.S2',
                )
    s.add_logical_signal("BAL", settings={"Nf": "true"})

    # D3/S3
    t2.add_detector(
            label=name+'.D3',
            position=200,
        )
    s = t2.add_signal(
                    220,
                    Direction.STOP_TO_START,
                    is_route_delimiter=True,
                    label=name+'.S3',
                )
    s.add_logical_signal("BAL", settings={"Nf": "true"})

    # D4/S4
    t2.add_detector(
            label=name+'.D4',
            position=820,
        )
    s = t2.add_signal(
                    800,
                    Direction.START_TO_STOP,
                    is_route_delimiter=True,
                    label=name+'.S4',
                )
    s.add_logical_signal("BAL", settings={"Nf": "true"})

    # D5
    track_out.add_detector(
            label=name+'.D5',
            position=20,
        )
    s = track_out.add_signal(
        40,
        Direction.STOP_TO_START,
        is_route_delimiter=True,
        label=name+'.S5',
    )
    s.add_logical_signal("BAL", settings={"Nf": "true"})

    station = infra_builder.add_operational_point(label=name+'.s')
    station.add_part(t1, 500)
    station.add_part(t2, 500)

    return track_out


def build_N_dvg_station_cvg(
    infra_builder: InfraBuilder,
    track_in: TrackSection,
    base_name: str,
    N: int
) -> TrackSection:
    """Create a serie of N stations (see build_dvg_station_cvg for details).

    All stations are created and connected one after the other. Their names
    are based on the base_name parameter with a numbered suffix.

    Parameters
    ----------
    infra_builder : InfraBuilder
        The InfraBuilder used to create.
    track_in : TrackSection
        The track the first station will be
        connected to.
    base_name : str
        The name to be used for all stations.
    N : int
        The number of station do be created.

    Returns
    -------
    TrackSection
        Return the last track section of all the stations.
    """
    track = track_in
    for i in range(0, N):
        track = build_dvg_station_cvg(
            infra_builder,
            track,
            base_name+"."+str(i)
        )

    return track
