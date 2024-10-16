import math

from haversine import (
    haversine,
    inverse_haversine,
    Direction as GeoDirection
)

from railjson_generator import (
    InfraBuilder
)
from railjson_generator.schema.infra.infra import TrackSection
from railjson_generator.schema.infra.direction import Direction


LENGTH_STATION = 800.
LENGTH_BLOCK = 1_500.
DISTANCE_SIGNAL_SWITCH = 50.
DISTANCE_SIGNAL_DETECTOR = 20.
LENGTH_ELBOW = 20
ANGLE_ELBOW = math.pi/16


def build_junction(
    infra_builder: InfraBuilder,
    track_in_short: TrackSection,
    track_in_long: TrackSection,
    length_before: float = 10,
    length_junction: float = 10,
    length_after: float = 10,
    geo_direction: GeoDirection | float = GeoDirection.EAST,
    long_ending: bool = True,
    short_ending: bool = True,
) -> tuple[TrackSection, TrackSection]:

    extend_track(track_in_short, length_before, geo_direction)
    extend_track(track_in_long, length_junction+length_before, geo_direction)

    junction = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=f'junction.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        line_name=track_in_short.line_name,
        line_code=track_in_short.line_code,
        length=length_junction,
    )

    junction.add_detector(
        position=junction.length/2,
        label=f'D.{junction.label}'
    )
    track_out_short = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_in_short.track_name,
        line_name=track_in_short.line_name,
        line_code=track_in_short.line_code,
        length=None,
    )
    track_out_long = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_in_long.track_name,
        line_name=track_in_long.line_name,
        line_code=track_in_long.line_code,
        length=None,
    )

    sw_short = infra_builder.add_point_switch(
        track_in_short.end(),
        junction.begin(),
        track_out_short.begin()
    )

    sw_short.set_coords(*track_in_short.coordinates[-1])

    sw_long = infra_builder.add_point_switch(
        track_out_long.begin(),
        track_in_long.end(),
        junction.end(),
    )
    sw_long.set_coords(*track_in_long.coordinates[-1])

    junction.length = haversine(
        track_in_short.coordinates[-1][::-1],
        track_out_long.coordinates[0][::-1],
        unit='m',
    )

    extend_track(track_out_short, length_junction+length_after, geo_direction, ending=short_ending)
    extend_track(track_out_long, length_after, geo_direction, ending=long_ending)

    return track_out_short, track_out_long



def add_carre_with_detector(
    track_section: TrackSection,
    position: float,
    direction: Direction,
    label: str,
) -> None:
    signal = track_section.add_signal(
        position,
        is_route_delimiter=True,
        label=f'CARRE.{label}',
        direction=direction,
    )
    signal.add_logical_signal("BAL", settings={"Nf": "true"})
    track_section.add_detector(
        label=f'D.{label}',
        position=signal.position + (
            DISTANCE_SIGNAL_DETECTOR
            if direction==Direction.START_TO_STOP
            else - DISTANCE_SIGNAL_DETECTOR
        )
    )


def add_semaphores_with_detector(
    track_section: TrackSection,
    position: float,
    label: str,
    forward: bool = True,
    backward: bool = False,
) -> None:

    if forward:
        track_section.add_signal(
            position - DISTANCE_SIGNAL_DETECTOR,
            is_route_delimiter=True,
            label=f'SEPHAMORE.{label}.1',
            direction=Direction.START_TO_STOP,
        ).add_logical_signal("BAL", settings={"Nf": "false"})
    if backward:
        track_section.add_signal(
            position + DISTANCE_SIGNAL_DETECTOR,
            is_route_delimiter=True,
            label=f'SEPHAMORE.{label}.2',
            direction=Direction.STOP_TO_START,
        ).add_logical_signal("BAL", settings={"Nf": "false"})

    track_section.add_detector(
        label=f'D.{label}',
        position=position
    )


def build_blocks(
    track: TrackSection,
    num_blocks: int,
    forward: bool = True,
    backward: bool = False,
    geo_direction: GeoDirection | float = GeoDirection.EAST,
) -> TrackSection:

    start_position = track.length
    extend_track(track=track, distance=num_blocks * LENGTH_BLOCK, geo_direction=geo_direction)
    if forward:
        add_carre_with_detector(
            track,
            position=track.length - DISTANCE_SIGNAL_SWITCH,
            direction=Direction.START_TO_STOP,
            label=f"{track.label}.end"
        )
    if backward:
        add_carre_with_detector(
            track,
            position=start_position + DISTANCE_SIGNAL_SWITCH,
            direction=Direction.STOP_TO_START,
            label=f"{track.label}.start"
        )
    for i in range(1, num_blocks):
        add_semaphores_with_detector(
            track_section=track,
            position=start_position +  i * LENGTH_BLOCK,
            label=f"{track.label}.{i}",
            forward=forward,
            backward=backward
        )


def _distance_from_start_is_increasing(
    coordinates: list[tuple[float, float]],
) -> bool:

    distances = [
        (c[1] - coordinates[0][1])**2 + (c[0] - coordinates[0][0])**2
        for c in coordinates
    ]

    return all(x<=y for x, y in zip(distances, distances[1:]))


def extend_track(
    track: TrackSection,
    distance: float,
    geo_direction: GeoDirection | float = GeoDirection.EAST,
    ending: bool = True
) -> None:

    if track.coordinates[-1] == (None, None):
        last_point_idx = -2
    else:
        last_point_idx = -1
    last_point = track.coordinates[last_point_idx]
    new_point = inverse_haversine(
        last_point[::-1],
        distance=distance,
        direction=geo_direction,
        unit='m'
    )

    if last_point_idx == -2:
        track.coordinates[-1] = tuple(new_point[::-1])
        track.length = distance
    else:
        track.coordinates.append(tuple(new_point[::-1]))
        track.length += distance

    if not _distance_from_start_is_increasing(track.coordinates):
        raise NotImplementedError(
            "Track sections path can not backtrack "
            "as it would cause problems with geo localisation on maps."""
        )

    if not ending:
        track.coordinates.append((None, None))

def build_station(
    infra_builder: InfraBuilder,
    track_in: TrackSection,
    station_name: str,
    forward: bool = True,
    backward: bool=False,
    track_names: list[str] = ['V1', 'V2'],
    curves: tuple[bool] = (True, True),
    geo_direction: GeoDirection | float = GeoDirection.EAST,
    bv_as_op: bool = True,
    length_after: float = 50.,
) -> TrackSection:
    v1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_names[0],
        line_name=track_in.line_name,
        line_code=track_in.line_code,
        length=LENGTH_STATION,
    )
    v2 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_names[1],
        line_name=track_in.line_name,
        line_code=track_in.line_code,
        length=LENGTH_STATION,
    )
    dvg = infra_builder.add_point_switch(
        track_in.end(),
        v1.begin(),
        v2.begin(),
    )

    dvg_coords_osrd = track_in.coordinates[-1]
    dvg.set_coords(*dvg_coords_osrd)
    
    cvg_coords = inverse_haversine(
        dvg_coords_osrd[::-1],
        LENGTH_STATION,
        geo_direction,
        unit='m'
    )

    track_out = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_in.track_name,
        line_name=track_in.line_name,
        line_code=track_in.line_code,
        length=None,
    )
        
    cvg = infra_builder.add_point_switch(
        track_out.begin(),
        v1.end(),
        v2.end(),
    )
    cvg.set_coords(*cvg_coords[::-1])
    
    extend_track(track_out, length_after, geo_direction)
    if curves[0]:
        v1_1_coords = inverse_haversine(
            dvg_coords_osrd[::-1],
            LENGTH_ELBOW,
            geo_direction - ANGLE_ELBOW,
            unit='m'
        )
        v1_2_coords = inverse_haversine(
            v1_1_coords,
            v1.length - 2 * LENGTH_ELBOW,
            geo_direction,
            unit='m'
        )
        v1.set_remaining_coords([v1_1_coords[::-1], v1_2_coords[::-1]])
        v1.length += haversine(cvg_coords, v1_2_coords, unit='m') - LENGTH_ELBOW

    if curves[1]:
        v2_1_coords = inverse_haversine(
                dvg_coords_osrd[::-1],
                LENGTH_ELBOW,
                geo_direction + ANGLE_ELBOW,
                unit='m'
            )
        v2_2_coords = inverse_haversine(
                v2_1_coords,
                v2.length - 2 * LENGTH_ELBOW,
                geo_direction,
                unit='m'
        )
        v2.set_remaining_coords([v2_1_coords[::-1], v2_2_coords[::-1]])
        v2.length += haversine(cvg_coords, v2_2_coords, unit='m') - LENGTH_ELBOW

    if forward:
        add_carre_with_detector(
            track_section=v1,
            position=v1.length - DISTANCE_SIGNAL_SWITCH,
            direction=Direction.START_TO_STOP,
            label=f'{station_name}.{track_names[0]}.e',
        )
        add_carre_with_detector(
            track_section=v2,
            position=v2.length - DISTANCE_SIGNAL_SWITCH,
            direction=Direction.START_TO_STOP,
            label=f'{station_name}.{track_names[1]}.e',
        )
        if not backward:
            v1.add_detector(
                position=DISTANCE_SIGNAL_SWITCH - DISTANCE_SIGNAL_DETECTOR,
                label=f'D.{station_name}.{track_names[0]}.s',
            )
            v2.add_detector(
                position=DISTANCE_SIGNAL_SWITCH - DISTANCE_SIGNAL_DETECTOR,
                label=f'D.{station_name}.{track_names[1]}.s',
            )
    if backward:
        add_carre_with_detector(
            track_section=v1,
            position=DISTANCE_SIGNAL_SWITCH,
            direction=Direction.STOP_TO_START,
            label=f'{station_name}.{track_names[0]}.s',
        )
        add_carre_with_detector(
            track_section=v2,
            position=DISTANCE_SIGNAL_SWITCH,
            direction=Direction.STOP_TO_START,
            label=f'{station_name}.{track_names[1]}.s',
        )
        if not forward:
            v1.add_detector(
                position=v1.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR,
                label=f'D.{station_name}.{track_names[0]}.e',
            )
            v2.add_detector(
                position=v1.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR,
                label=f'D.{station_name}.{track_names[1]}.e',
            )
    if bv_as_op:
        bv = infra_builder.add_operational_point(station_name)
        bv.add_part(v1, LENGTH_STATION/2)
        bv.add_part(v2, LENGTH_STATION/2)

    return track_out


def build_station_3_5(
    infra_builder: InfraBuilder,
    track_in: TrackSection,
    track_inout: TrackSection,
    track_out: TrackSection,
    station_name: str,
    geo_direction: GeoDirection | float = GeoDirection.EAST,
    signals_after: bool = True
) -> tuple[TrackSection, TrackSection, TrackSection]:

    extend_track(track_in, 60, geo_direction)
    extend_track(track_inout, 60, geo_direction)
    extend_track(track_out, 60, geo_direction)

    add_carre_with_detector(
        track_in,
        position=track_in.length - DISTANCE_SIGNAL_SWITCH,
        label=f"entree_gare.{station_name}.1bis",
        direction=Direction.START_TO_STOP,
    )
    add_carre_with_detector(
        track_inout,
        position=track_inout.length - DISTANCE_SIGNAL_SWITCH,
        label=f"entree_gare.{station_name}.1",
        direction=Direction.START_TO_STOP,
    )

    track_inout, track_out = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_inout,
        track_in_long=track_out,
        geo_direction=geo_direction,
        length_after=5,
        length_before=5,
        length_junction=20
    )
    extend_track(track_in, 30, geo_direction)
    track_inout.add_detector(DISTANCE_SIGNAL_DETECTOR)
    track_out.add_detector(DISTANCE_SIGNAL_DETECTOR)

    track_inout, track_in = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_inout,
        track_in_long=track_in,
        geo_direction=geo_direction,
        length_after=5,
        length_before=5,
        length_junction=20
    )
    extend_track(track_out, 30, geo_direction)
    track_in.add_detector(5)
    track_inout.add_detector(DISTANCE_SIGNAL_DETECTOR)

    track_in, track_inout = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_in,
        track_in_long=track_inout,
        geo_direction=geo_direction,
        length_after=5,
        length_before=5,
        length_junction=20
    )
    extend_track(track_out, 30, geo_direction)
    track_in.add_detector(DISTANCE_SIGNAL_DETECTOR)
    track_inout.add_detector(5)

    track_out, track_inout = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_out,
        track_in_long=track_inout,
        geo_direction=geo_direction,
        length_after=15,
        length_before=5,
        length_junction=20
    )
    extend_track(track_in, 40, geo_direction)
    track_out.add_detector(20)

    track_in = build_station(
        infra_builder=infra_builder,
        track_in=track_in,
        station_name=station_name,
        geo_direction=geo_direction,
        curves=(True, False),
        track_names=['V4', 'V2'],
        bv_as_op=False,
        length_after=10
    )
    v2 = infra_builder.infra.track_sections[-3]
    v4 = infra_builder.infra.track_sections[-2]

    track_out = build_station(
        infra_builder=infra_builder,
        track_in=track_out,
        station_name=station_name,
        geo_direction=geo_direction,
        curves=(False, True),
        track_names=['V3', 'V5'],
        forward=False,
        backward=True,
        bv_as_op=False,
        length_after=10
    )
    v5 = infra_builder.infra.track_sections[-3]
    v3 = infra_builder.infra.track_sections[-2]

    station = infra_builder.add_operational_point(station_name)
    for v in [v2, v3, v4, v5]:
        station.add_part(v, v.length/2)

    extend_track(track_inout, 810, geo_direction)
    station.add_part(track_inout, 415)

    add_carre_with_detector(
        track_inout,
        position=65,
        direction=Direction.STOP_TO_START,
        label=f'{station_name}.{track_inout.track_name}.s'
    )
    add_carre_with_detector(
        track_inout,
        position=765,
        direction=Direction.START_TO_STOP,
        label=f'{station_name}.{track_inout.track_name}.e'
    )

    track_out.add_detector(position=10)
    track_inout, track_out = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_inout,
        track_in_long=track_out,
        geo_direction=geo_direction,
        length_after=5,
        length_before=5,
        length_junction=20
    )
    extend_track(track_in, 30, geo_direction,)
    track_inout.add_detector(20)

    track_in.add_detector(30)
    track_inout, track_in = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_inout,
        track_in_long=track_in,
        geo_direction=geo_direction,
        length_after=5,
        length_before=5,
        length_junction=20
    )
    extend_track(track_out, 30, geo_direction)
    track_in.add_detector(5)
    track_inout.add_detector(20)
    track_out.add_detector(30)

    track_in, track_inout = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_in,
        track_in_long=track_inout,
        geo_direction=geo_direction,
        length_after=5,
        length_before=5,
        length_junction=20
    )
    extend_track(track_out, 30, geo_direction)
    track_inout.add_detector(5)
    track_in.add_detector(25)

    track_out, track_inout = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_out,
        track_in_long=track_inout,
        geo_direction=geo_direction,
        length_after=55,
        length_before=5,
        length_junction=20
    )
    extend_track(track_in, 80, geo_direction)

    if signals_after:
        add_carre_with_detector(
            track_inout,
            position=DISTANCE_SIGNAL_SWITCH,
            direction=Direction.STOP_TO_START,
            label=f"sortie_gare.{station_name}.1"
        )
        add_carre_with_detector(
            track_out,
            position=DISTANCE_SIGNAL_SWITCH,
            direction=Direction.STOP_TO_START,
            label=f"entree_gare.{station_name}.2"
    )

    return track_in, track_inout, track_out

def build_terminal_station_3_5(
    infra_builder: InfraBuilder,
    track_in: TrackSection,
    track_inout: TrackSection,
    track_out: TrackSection,
    station_name: str,
    geo_direction: GeoDirection | float,
) -> tuple[TrackSection, TrackSection, TrackSection, TrackSection, TrackSection]:
    
    line_name = track_inout.line_name
    line_code = track_inout.line_code

    extend_track(track_in, 50, geo_direction=geo_direction)
    extend_track(track_inout, 50, geo_direction=geo_direction)
    extend_track(track_out, 50, geo_direction=geo_direction)

    add_carre_with_detector(
        track_in,
        10,
        direction=Direction.START_TO_STOP,
        label=f'{station_name}.in'
    )
    add_carre_with_detector(
        track_inout,
        10,
        direction=Direction.START_TO_STOP,
        label=f'{station_name}.inout'
    )

    v4, track_inout = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_out,
        track_in_long=track_inout,
        geo_direction=geo_direction,
        length_before=5,
        length_after=5,
        length_junction=20
    )
    v4.track_name = 'V4'
    extend_track(track_in, 30, geo_direction=geo_direction)
    v4.add_detector(40)
    track_inout.add_detector(10)

    v5, track_inout = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_in,
        track_in_long=track_inout,
        geo_direction=geo_direction,
        length_before=5,
        length_after=5,
        length_junction=20
    )
    v5.add_detector(30)
    v5.track_name = 'V5'
    extend_track(v4, 20, geo_direction=geo_direction)

    extend_track(v5, LENGTH_ELBOW, geo_direction=geo_direction-ANGLE_ELBOW)
    extend_track(v5, 10, geo_direction=geo_direction)

    extend_track(v4, LENGTH_ELBOW, geo_direction=geo_direction+ANGLE_ELBOW)
    extend_track(v4, 30, geo_direction=geo_direction)

    extend_track(track_inout, 10, ending=False, geo_direction=geo_direction)
    track_inout.add_detector(track_inout.length/2)

    t_13 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='J13',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    v3 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V3',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    v1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    v2 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    sw_213 = infra_builder.add_point_switch(
        track_inout.end(),
        t_13.begin(),
        v3.begin()
    )
    sw_213.set_coords(
        *track_inout.coordinates[-2]
    )
    
    extend_track(v3, LENGTH_ELBOW, geo_direction=geo_direction-ANGLE_ELBOW)
    v3.add_detector(v3.length/2)

    v3, v5 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v3,
        track_in_long=v5,
        geo_direction=geo_direction,
        length_before=5,
        length_after=LENGTH_STATION/2,
        length_junction=20
    )

    extend_track(t_13, LENGTH_ELBOW, geo_direction=geo_direction+ANGLE_ELBOW, ending=False)
    t_13.add_detector(t_13.length/2)
    sw_13 = infra_builder.add_point_switch(
        t_13.end(),
        v1.begin(),
        v2.begin()
    )
    sw_13.set_coords(
        *t_13.coordinates[-2]
    )

    extend_track(v1, LENGTH_ELBOW, geo_direction=geo_direction-ANGLE_ELBOW)
    extend_track(v1, LENGTH_STATION/2+5, geo_direction=geo_direction)
    
    extend_track(v2, 10, geo_direction=geo_direction)
    v2.add_detector(v2.length/2)

    v2, v4 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v2,
        track_in_long=v4,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=geo_direction
    )
    extend_track(v2, LENGTH_STATION/2-15, geo_direction=geo_direction)
    extend_track(v4, LENGTH_STATION/2-15, geo_direction=geo_direction)

    station = infra_builder.add_operational_point(station_name)

    for i, v in enumerate([v1, v3, v2, v5, v4]):
        add_carre_with_detector(
            v,
            v.length-100.,
            direction=Direction.STOP_TO_START,
            label=f'{station_name}.{i+1}'

        )
        v.add_buffer_stop(v.length, label=f'bs.{station_name}.{i+1}')
        station.add_part(v, v.length-80)

    return v1, v3, v2, v5, v4


def build_terminal_station_2_4(
    infra_builder: InfraBuilder,
    track_in: TrackSection,
    track_out: TrackSection,
    station_name: str,
    geo_direction: GeoDirection | float
) -> None:
    
    track_out.add_detector(track_out.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR)
    
    track_in, track_out = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_in,
        track_in_long=track_out,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=geo_direction,
    )
    track_out.add_detector(5)
    track_in.add_detector(25)
    track_out, track_in = build_junction(
        infra_builder=infra_builder,
        track_in_short=track_out,
        track_in_long=track_in,
        length_before=5,
        length_junction=20,
        length_after=15,
        geo_direction=geo_direction,
    )
    track_in.add_detector(5)
    track_out.add_detector(25)

    v4 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=f"V{int(track_in.track_name.replace('V','').replace('bis', ''))+2}",
        line_name=track_in.line_name,
        line_code=track_in.line_code,
        length=None,
    )
    v2 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_in.track_name,
        line_name=track_in.line_name,
        line_code=track_in.line_code,
        length=None,
    )
    sw_in = infra_builder.add_point_switch(
        track_in.end(),
        v4.begin(),
        v2.begin()
    )
    sw_in.set_coords(*track_in.coordinates[-1])
    extend_track(v4, LENGTH_ELBOW, geo_direction - ANGLE_ELBOW)
    extend_track(v2, LENGTH_ELBOW, geo_direction)

    v3 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=f"V{int(track_out.track_name.replace('V','').replace('bis', ''))+2}",
        line_name=track_out.line_name,
        line_code=track_out.line_code,
        length=None,
    )
    v1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name=track_out.track_name,
        line_name=track_out.line_name,
        line_code=track_out.line_code,
        length=None,
    )
    sw_out = infra_builder.add_point_switch(
        track_out.end(),
        v3.begin(),
        v1.begin()
    )
    sw_out.set_coords(*track_out.coordinates[-1])
    extend_track(v3, LENGTH_ELBOW, geo_direction + ANGLE_ELBOW)
    extend_track(v1, LENGTH_ELBOW, geo_direction)

    v1.add_detector(LENGTH_ELBOW)
    v2.add_detector(LENGTH_ELBOW)

    v1, v2 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v1,
        track_in_long=v2,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=geo_direction
    )
    v2, v1 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v2,
        track_in_long=v1,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=geo_direction
    )
    extend_track(v1, LENGTH_STATION - 60, geo_direction)
    extend_track(v2, LENGTH_STATION - 60, geo_direction)

    for track in [v1, v2, v1, v2]:
        length= 0
        for i, _ in enumerate(track.coordinates):
            if i > 0:
                length += round(haversine(
                        track.coordinates[i][::-1],
                        track.coordinates[i-1][::-1],
                        unit='m'
                    ), 2)
        track.length = length

    extend_track(v3, LENGTH_STATION, geo_direction)
    extend_track(v4, LENGTH_STATION, geo_direction)

    station = infra_builder.add_operational_point(station_name)
    for v in [v1, v2, v3, v4]:
        add_carre_with_detector(
            v,
            100,
            direction=Direction.STOP_TO_START,
            label=f"{station_name}.{v.track_name}"
        )
        station.add_part(v, 550)
