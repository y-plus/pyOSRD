import math
import os

from haversine import inverse_haversine, haversine, Direction as GeoDirection

from railjson_generator import (
    InfraBuilder,
)
from railjson_generator.schema.infra.infra import Infra
from railjson_generator.schema.infra.direction import Direction

from pyosrd.infra.build import build_infra

from pyosrd.use_cases.infras.helpers.builders import (
    build_junction,
    add_carre_with_detector,
    add_semaphores_with_detector,
    build_blocks,
    build_station,
    extend_track,
    build_station_3_5,
    build_terminal_station_3_5,
    build_terminal_station_2_4
)

def hamelinfra(
    dir: str,
    infra_json: str = 'infra.json',
) -> Infra:
    """
    
    """  # noqa

    LENGTH_STATION = 800.
    DISTANCE_SIGNAL_SWITCH = 50.
    DISTANCE_SIGNAL_DETECTOR = 20.
    LENGTH_ELBOW = 20
    ANGLE_ELBOW = math.pi/16
    
    infra_builder = InfraBuilder()
    
    
    # Ligne ABC
    line_name="A-B-C"
    line_code=1_000

    t0 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='VU',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    BEGIN = (45.575988410701974, 0.21)
    t0.coordinates[0] = tuple(BEGIN[::-1])
    extend_track(t0, 1_500, geo_direction=GeoDirection.EAST)

    add_carre_with_detector(
        t0,
        position=t0.length - DISTANCE_SIGNAL_SWITCH,
        direction=Direction.START_TO_STOP,
        label=f"{'A'}_entrance"
    )

    track = build_station(
        infra_builder=infra_builder,
        track_in=t0,
        station_name='A',
        forward=True,
        backward=True,
        track_names=['V2', 'V1']
    )
    build_blocks(
        track,
        num_blocks=6,
        forward=True,
        backward=True,
    )
    
    track = build_station(
        infra_builder=infra_builder,
        track_in=track,
        station_name='B',
        forward=True,
        backward=True,
        track_names=['V2', 'V1']
    )

    build_blocks(
        track,
        num_blocks=6,
        forward=True,
        backward=True,
    )

    t2 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
        line_name=line_name,
        line_code=line_code,
        length=None,  
    ) 
    t1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1',
        line_name=line_name,
        line_code=line_code,
        length=None,  
    )

    sw1bis = infra_builder.add_point_switch(
        track.end(),
        t1.begin(),
        t2.begin()
    )
    sw1bis.set_coords(*track.coordinates[-1])
    extend_track(t1, LENGTH_ELBOW/2, GeoDirection.EAST+ANGLE_ELBOW)
    extend_track(t2, LENGTH_ELBOW/2, GeoDirection.EAST-ANGLE_ELBOW)

    build_blocks(
        t2,
        num_blocks=1,
        forward=True,
        backward=False,
        geo_direction=GeoDirection.EAST,
    )
    t2.add_detector(
        position = DISTANCE_SIGNAL_SWITCH - DISTANCE_SIGNAL_DETECTOR,
        label=f"D.{t2.label}.dvg"
    )
    build_blocks(
        t1,
        num_blocks=1,
        forward=False,
        backward=True,
        geo_direction=GeoDirection.EAST
    )
       
    t1 = build_station(
        infra_builder=infra_builder,
        track_in=t1,
        station_name='C',
        forward=False,
        backward=True,
        track_names=['V1', 'V3'],
        bv_as_op=False,
        curves=(False, True)
    )
    v1 = infra_builder.infra.track_sections[-3]
    v3 = infra_builder.infra.track_sections[-2]
   
    t2 = build_station(
        infra_builder=infra_builder,
        track_in=t2,
        station_name='D',
        forward=True,
        backward=False,
        track_names=['V4', 'V2'],
        bv_as_op=False,
        curves=(True, False)
    )
    v2 = infra_builder.infra.track_sections[-3]
    v4 = infra_builder.infra.track_sections[-2]

    c = infra_builder.add_operational_point('C')
    for v in [v1, v2, v3, v4]:
        c.add_part(v, LENGTH_STATION/2)

    build_blocks(
        t2,
        num_blocks=6,
        forward=True,
        backward=False,
        geo_direction=3*math.pi/8
    )
   

    build_blocks(
        t1,
        num_blocks=6,
        forward=False,
        backward=True,
        geo_direction=3*math.pi/8
    )

# #Sortie pont

    bridge_t1 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='BRIDGE',
        line_name=line_name,
        line_code=line_code,
        length=None,  
    )
    

    link = infra_builder.add_link(
        t1.end(),
        bridge_t1.begin(),
        label='bridge.out'
    )
    link.set_coords(*t1.coordinates[-1])

    
    # add_semaphores_with_detector(
    #     bridge_t1,
    #     DISTANCE_SIGNAL_SWITCH,
    #     backward=True,
    #     forward=False,
    #     label='t1'
    # )
    extend_track(t2, DISTANCE_SIGNAL_SWITCH, 3*math.pi/8)
    extend_track(bridge_t1, DISTANCE_SIGNAL_SWITCH, 3*math.pi/8)

    t2, bridge_t1 = build_junction(
        infra_builder=infra_builder,
        track_in_short=t2,
        track_in_long=bridge_t1,
        length_before=25,
        length_junction=20,
        length_after=15,
        geo_direction=3*math.pi/8,
    )
    t2.add_detector(30)
    bridge_t1.add_detector(10)
    extend_track(bridge_t1, 10, 3*math.pi/8)

    ####################

    bridge = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='BRIDGE',
        line_name=line_name,
        line_code=line_code,
        length=None,  
    )

    connection_c_d = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='CONNECTION',
        line_name='CONNECTION',
        line_code=line_code,
        length=None,  
    )
    
    sw_connection_west = infra_builder.add_point_switch(
        bridge_t1.end(),
        connection_c_d.begin(),
        bridge.begin()
    )
    sw_connection_west.set_coords(*bridge_t1.coordinates[-1])

    add_carre_with_detector(
        connection_c_d,
        DISTANCE_SIGNAL_SWITCH, 
        Direction.STOP_TO_START,
        label='connection_CD_east'
    )
    add_carre_with_detector(
        bridge,
        DISTANCE_SIGNAL_SWITCH, 
        Direction.STOP_TO_START,
        label='bridge_out'
    )

    extend_track(connection_c_d, LENGTH_ELBOW, 3*math.pi/8+ANGLE_ELBOW)
    extend_track(connection_c_d, 900, 3*math.pi/8)
    extend_track(connection_c_d, 350, GeoDirection.EAST)
    extend_track(connection_c_d, 100, 5*math.pi/8, ending=False)
    
    extend_track(t2, 1_500, 3*math.pi/8)
    extend_track(bridge, 1_500, 3*math.pi/8)


    # # Ligne E-I
    line_name="E-I"
    line_code = 2000


    v2_south = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
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
    
    add_carre_with_detector(
        t2,
        t2.length - DISTANCE_SIGNAL_SWITCH,
        Direction.START_TO_STOP,
        label='raccord-CD'
    )
    sw2 = infra_builder.add_point_switch(
        v2.begin(),
        t2.end(),
        v2_south.begin()
    )
    sw2.set_coords(*t2.coordinates[-1])

    v1_south = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1',
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

    sw1 = infra_builder.add_link(
        v1.begin(),
        v1_south.begin(),
        label='link.v1.north_south'
    )
    sw1.set_coords(*inverse_haversine(
            t2.coordinates[-1][::-1],
            2.5,
            GeoDirection.EAST,
            unit='m'
        )[::-1]
    )

    v1bis_south = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1bis',
        line_name=line_name,
        line_code=line_code,
        length=None,  
    )

    v1bis = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1bis',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    sw1bis = infra_builder.add_link(
        v1bis.begin(),
        v1bis_south.begin(),
        label='link.v1bis.north_south'
    )
    sw1bis.set_coords(*inverse_haversine(
            t2.coordinates[-1][::-1],
            5.,
            GeoDirection.EAST,
            unit='m'
        )[::-1]
    )

    # # South Station

    extend_track(v1bis_south, 400, GeoDirection.SOUTH)
    extend_track(v1_south, 400, GeoDirection.SOUTH)
    extend_track(v2_south, 400, GeoDirection.SOUTH)

    v2_south_2 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1bis',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )

    sw_connection_south = infra_builder.add_point_switch(
        v2_south_2.begin(),
        v2_south.end(),
        connection_c_d.end()
    )

    sw_connection_south.set_coords(*v2_south.coordinates[-1])

    connection_c_d.length += haversine(
        connection_c_d.coordinates[-2][::-1],
        connection_c_d.coordinates[-1][::-1],
        unit='m',
    )


    connection_c_d.add_detector(connection_c_d.length - DISTANCE_SIGNAL_SWITCH)
    v2_south.add_detector(v2_south.length - DISTANCE_SIGNAL_SWITCH)
    v2_south_2.add_detector(30)

    build_terminal_station_3_5(
        infra_builder=infra_builder,
        track_in=v1bis_south,
        track_inout=v1_south,
        track_out=v2_south_2,
        station_name='D',
        geo_direction=GeoDirection.SOUTH
    )

    # # North
    extend_track(v2, 20, GeoDirection.NORTH)
    extend_track(v1bis, 20, GeoDirection.NORTH)
    extend_track(v1, 20, GeoDirection.NORTH)

    v2.add_detector(10)

    v2, v1 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v2,
        track_in_long=v1,
        length_before=20,
        length_junction=20,
        length_after=690,
        geo_direction=GeoDirection.NORTH
    )
    v2.add_detector(20)
    extend_track(v1bis, 720, GeoDirection.NORTH)

    

    # Connexion pont-v1
    extend_track(bridge, 700, GeoDirection.NORTH, ending=False)

    new_v1bis = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1bis',
        line_name=line_name,
        line_code=line_code,
        length=None,
    )
    bridge_in = infra_builder.add_point_switch(
        new_v1bis.begin(),
        bridge.end(),
        v1bis.end(),
        label='bridge.in'
    )
    bridge.length += haversine(
        bridge.coordinates[-2][::-1],
        v1bis.coordinates[-1][::-1],
        unit='m'
    )
    bridge_in.set_coords(
        *v1bis.coordinates[-1]
    )
    bridge.add_detector(
        bridge.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR
    )
    v1bis.add_detector(
        v1bis.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR
    )
    v1bis = new_v1bis
    extend_track(v1bis, 10, GeoDirection.NORTH)

    v1bis.add_detector(v1bis.length/2)
    v1.add_detector(v1.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR)
    v1bis, v1 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v1bis,
        track_in_long=v1,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=GeoDirection.NORTH
    )
    extend_track(v2, 30, GeoDirection.NORTH)

    for station in ['E', 'F', 'G']:
        build_blocks(
            v1bis,
            num_blocks=6,
            forward=False,
            backward=True,
            geo_direction=GeoDirection.NORTH,
        )
        build_blocks(
            v1,
            num_blocks=6,
            forward=True,
            backward=True,
            geo_direction=GeoDirection.NORTH,
        )
        build_blocks(
            v2,
            num_blocks=6,
            forward=True,
            backward=False,
            geo_direction=GeoDirection.NORTH,
        )

        v2, v1, v1bis = build_station_3_5(
            infra_builder=infra_builder,
            track_in=v2,
            track_inout=v1,
            track_out=v1bis,
            station_name=station,
            geo_direction=GeoDirection.NORTH,
            signals_after=False
        )
    v1.add_detector(v1.length/2)

    v1, v2 = build_junction(
        infra_builder=infra_builder,
        track_in_short=v1,
        track_in_long=v2,
        geo_direction=GeoDirection.NORTH,
        length_before=5,
        length_junction=20,
        length_after=5
    )
    extend_track(v1bis, 30, GeoDirection.NORTH)

    v2west = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
        line_name='H-I',
        line_code=3_000,
        length=None,
    )
    v1west = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1',
        line_name='H-I',
        line_code=3_000,
        length=None,
    )

    v2east = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V2',
        line_name='G-K',
        line_code=4_000,
        length=None,
    )
    v1east = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V1',
        line_name='G-K',
        line_code=4_000,
        length=None,
    )

    link_west = infra_builder.add_link(
        v2.end(),
        v2west.begin()
    )
    link_west.set_coords(*v2.coordinates[-1])
    extend_track(v2west, 100, geo_direction=GeoDirection.NORTHWEST)

    link_east = infra_builder.add_link(
        v1bis.end(),
        v1east.begin()
    )
    link_east.set_coords(*v1bis.coordinates[-1])
    extend_track(v1east, 100, geo_direction=GeoDirection.NORTHEAST)

    extend_track(v1, 2, GeoDirection.NORTH)
    v1.add_detector(v1.length/2)


    sw2 = infra_builder.add_point_switch(
        v1.end(),
        v2east.begin(),
        v1west.begin(),
    )
    sw2.set_coords(*v1.coordinates[-1])
    extend_track(v1west, 100, geo_direction=GeoDirection.NORTHWEST)
    extend_track(v2east, 100, geo_direction=GeoDirection.NORTHEAST)
    v2east.add_detector(
        DISTANCE_SIGNAL_SWITCH - DISTANCE_SIGNAL_DETECTOR
    )
    
    # ## NORTH EAST BRANCH

    build_blocks(
        v2east,
        num_blocks=6,
        forward=True,
        backward=False,
        geo_direction=GeoDirection.NORTHEAST,
    )
    build_blocks(
        v1east,
        num_blocks=6,
        forward=False,
        backward=True,
        geo_direction=GeoDirection.NORTHEAST,
    )

    station_j_start = v1east.coordinates[-1]

    v2east = build_station(
        infra_builder=infra_builder,
        track_in=v2east,
        station_name='J',
        forward=True,
        backward=False,
        track_names=['V4', 'V2'],
        bv_as_op=False,
        curves=(True, False),
        geo_direction=GeoDirection.NORTHEAST
    )
    v4 = infra_builder.infra.track_sections[-2]
    v2 = infra_builder.infra.track_sections[-3]


    v1east = build_station(
        infra_builder=infra_builder,
        track_in=v1east,
        station_name='J',
        forward=False,
        backward=True,
        track_names=['V1', 'V3'],
        bv_as_op=False,
        curves=(False, True),
        geo_direction=GeoDirection.NORTHEAST
    )
    v1 = infra_builder.infra.track_sections[-3]
    v3 = infra_builder.infra.track_sections[-2]

    station_j = infra_builder.add_operational_point('J')
    for v in [v1, v2, v3, v4]:
        station_j.add_part(v, LENGTH_STATION/2)

    build_blocks(
        v2east,
        num_blocks=6,
        forward=True,
        backward=False,
        geo_direction=GeoDirection.NORTHEAST,
    )
    build_blocks(
        v1east,
        num_blocks=6,
        forward=False,
        backward=True,
        geo_direction=GeoDirection.NORTHEAST,
    )
    v1east.add_detector(v1east.length - DISTANCE_SIGNAL_SWITCH + DISTANCE_SIGNAL_DETECTOR)
    v1east, v2east = build_junction(
        infra_builder=infra_builder,
        track_in_short=v1east,
        track_in_long=v2east,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=GeoDirection.NORTHEAST
    )
    v2east.add_detector(5)
    v1east.add_detector(10)
    v2east, v1east = build_junction(
        infra_builder=infra_builder,
        track_in_short=v2east,
        track_in_long=v1east,
        length_before=5,
        length_junction=20,
        length_after=5,
        geo_direction=GeoDirection.NORTHEAST
    )

    extend_track(v2east, LENGTH_STATION, geo_direction=GeoDirection.NORTHEAST)
    extend_track(v1east, LENGTH_STATION, geo_direction=GeoDirection.NORTHEAST)
    add_carre_with_detector(
        v2east,
        400,
        Direction.STOP_TO_START,
        label='K.1'
    )
    add_carre_with_detector(
        v1east,
        400,
        Direction.STOP_TO_START,
        label='K.2'
    )
    station_k = infra_builder.add_operational_point('K')
    station_k.add_part(v2east, 600)
    station_k.add_part(v1east, 600)

    # # # BRANCHE EST = Ligne J-L

    v6 = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='V6',
        line_name='J-L',
        line_code=5_000,
        length=None,
    )
    v6.coordinates[0] = inverse_haversine(
        station_j_start[::-1],
        30,
        direction=GeoDirection.EAST,
        unit='m'
    )[::-1]

    extend_track(v6, LENGTH_STATION, GeoDirection.NORTHEAST)
    station_j.add_part(v6, 400)


    v2east = infra_builder.add_track_section(
        label=f'track.{str(len(infra_builder.infra.track_sections)).zfill(3)}',
        track_name='VU',
        line_name='J-L',
        line_code=5_000,
        length=None,
    )
    link = infra_builder.add_link(v6.end(), v2east.begin())
    link.set_coords(*v6.coordinates[-1])
    extend_track(v2east, 100, 7*math.pi/16)
    build_blocks(
        v2east,
        num_blocks=6,
        forward=True,
        backward=True,
        geo_direction=GeoDirection.EAST
    )
    extend_track(v2east, LENGTH_STATION, GeoDirection.EAST)

    station_l = infra_builder.add_operational_point('L')
    station_l.add_part(v2east, v2east.length - LENGTH_STATION/2)


    # ## NORTH WEST BRANCH

    build_blocks(
        v2west,
        num_blocks=6,
        forward=True,
        backward=False,
        geo_direction=GeoDirection.NORTHWEST,
    )
    build_blocks(
        v1west,
        num_blocks=6,
        forward=False,
        backward=True,
        geo_direction=GeoDirection.NORTHWEST,
    )

    v2west = build_station(
        infra_builder=infra_builder,
        track_in=v2west,
        station_name='H',
        forward=True,
        backward=False,
        track_names=['V4', 'V2'],
        bv_as_op=False,
        curves=(True, False),
        geo_direction=GeoDirection.NORTHWEST
    )
    v4 = infra_builder.infra.track_sections[-2]
    v2 = infra_builder.infra.track_sections[-3]


    v1west = build_station(
        infra_builder=infra_builder,
        track_in=v1west,
        station_name='H',
        forward=False,
        backward=True,
        track_names=['V1', 'V3'],
        bv_as_op=False,
        curves=(False, True),
        geo_direction=GeoDirection.NORTHWEST
    )
    v1 = infra_builder.infra.track_sections[-3]
    v3 = infra_builder.infra.track_sections[-2]

    station_i = infra_builder.add_operational_point('H')
    for v in [v1, v2, v3, v4]:
        station_i.add_part(v, LENGTH_STATION/2)

    build_blocks(
        v2west,
        num_blocks=6,
        forward=True,
        backward=False,
        geo_direction=GeoDirection.NORTHWEST,
    )
    build_blocks(
        v1west,
        num_blocks=6,
        forward=False,
        backward=True,
        geo_direction=GeoDirection.NORTHWEST,
    )

    build_terminal_station_2_4(
        infra_builder=infra_builder,
        track_in=v2west,
        track_out=v1west,
        station_name='I',
        geo_direction=GeoDirection.NORTHWEST
    )

    ## Build and save

    os.makedirs(dir, exist_ok=True)

    built_infra = build_infra(
        infra_builder,
    )
    built_infra.save(os.path.join(dir, infra_json))

    return built_infra

