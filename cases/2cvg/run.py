import os
import sys
sys.path.append("/home/renan/osrd/core/examples/generated/lib/")

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    ApplicableDirection,
    Location,
)
from railjson_generator.schema.infra.direction import Direction

builder = InfraBuilder()

WEST_Q1 = builder.add_track_section(label='WEST_Q1', length=450)
WEST_Q2 = builder.add_track_section(label='WEST_Q2', length=450)

T1 = builder.add_track_section(label='T1', length=10_000.)
T2 = builder.add_track_section(label='T2', length=10_000.)
builder.add_link(T1.end(), T2.begin(), Direction.START_TO_STOP)

builder.add_point_switch(T1.begin(), WEST_Q1.end(), WEST_Q2.end(), label='CVG')


DA1 = WEST_Q1.add_detector(position=430, label='DA1')
DA2 = WEST_Q2.add_detector(position=430, label='DA2')
SA1 = WEST_Q1.add_signal(DA1.position-20, Direction.START_TO_STOP, DA1)
SA2 = WEST_Q2.add_signal(DA2.position-20, Direction.START_TO_STOP, DA2)
DA_out = T1.add_detector(position=50, label='DA_out')
SA_OUT = T1.add_signal(DA_out.position-20, Direction.START_TO_STOP, DA_out)

EAST_Q1 = builder.add_track_section(label='EAST_Q1', length=450)
EAST_Q2 = builder.add_track_section(label='EAST_Q2', length=450)

builder.add_point_switch(T2.end(), EAST_Q1.begin(), EAST_Q2.begin(), label='DVG')

DB_in = T2.add_detector(position=T2.length-30, label='DB_in')
DB1 = EAST_Q1.add_detector(position=30, label='DB1')
DB2 = EAST_Q2.add_detector(position=30, label='DB2')
SB_in = T2.add_signal(DB_in.position-20, Direction.START_TO_STOP, DB_in)
SB1 = EAST_Q1.add_signal(DB1.position-20, Direction.START_TO_STOP, DB1)
SB2 = EAST_Q2.add_signal(DB2.position-20, Direction.START_TO_STOP, DB2)

# WEST_Q1.add_buffer_stop(position=0, applicable_direction=ApplicableDirection.START_TO_STOP)
# WEST_Q2.add_buffer_stop(position=0, applicable_direction=ApplicableDirection.START_TO_STOP)
# EAST_Q1.add_buffer_stop(position=EAST_Q1.length, applicable_direction=ApplicableDirection.START_TO_STOP)
# EAST_Q2.add_buffer_stop(position=EAST_Q2.length, applicable_direction=ApplicableDirection.START_TO_STOP)

D, S = [], []
for pos in range(5):
    D.append(T1.add_detector(position=1980.*(1+pos), label=f"D{str(pos)}"))
    T1.add_signal(D[pos].position-20, Direction.START_TO_STOP, D[pos])
for pos in range(4):
    D.append(T2.add_detector(position=1980.*(1+pos), label=f"D{str(5+pos)}"))
    T2.add_signal(D[5+pos].position-20, Direction.START_TO_STOP, D[5+pos])


SOUTH_Q1 = builder.add_track_section(label='SOUTH_Q1', length=450)
builder.add_point_switch(
    T2.begin(),
    T1.end(),
    SOUTH_Q1.end(),
    label='CVG2'
)
# SOUTH_Q1.add_buffer_stop(position=0, applicable_direction=ApplicableDirection.START_TO_STOP)
DS1 = SOUTH_Q1.add_detector(position=430, label='DS1')
SA1 = SOUTH_Q1.add_signal(DS1.position-20, Direction.START_TO_STOP, DS1)

infra = builder.build()


builder = SimulationBuilder(infra)

train0 = builder.add_train_schedule(
    Location(WEST_Q1, 400),
    Location(EAST_Q1, 440),
    label='train0',
    departure_time=0,
    # rolling_stock="short_fast_rolling_stock",
)
# train0.add_stop(100, location=Location(T1, 4500))


train1 = builder.add_train_schedule(
    Location(SOUTH_Q1, 400),
    Location(EAST_Q2, 440),
    label='train1',
    departure_time=300,
    # rolling_stock="short_fast_rolling_stock"
)

train2 = builder.add_train_schedule(
    Location(WEST_Q2, 400),
    Location(EAST_Q2, 440),
    label='train0',
    departure_time=600,
    # rolling_stock="short_fast_rolling_stock",
)
# train0.add_stop(100, location=Location(T1, 4500))


sim = builder.build()


infra.save("infra.json")
sim.save('simulation.json')
os.system("java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path infra.json --sim_path simulation.json --res_path results.json")
