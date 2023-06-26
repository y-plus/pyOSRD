import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction

builder = InfraBuilder()

STA_Q1 = builder.add_track_section(label='STA_Q1', length=450)
STA_Q2 = builder.add_track_section(label='STA_Q2', length=450)

T = builder.add_track_section(label='T', length=10_000.)

builder.add_point_switch(T.begin(), STA_Q1.end(), STA_Q2.end(), label='CVG')
# builder.add_link(STA_Q1.end(), T.begin())

DA1 = STA_Q1.add_detector(position=430, label='DA1')
DA2 = STA_Q2.add_detector(position=430, label='DA2')
SA1 = STA_Q1.add_signal(DA1.position-20, Direction.START_TO_STOP, DA1, label='SA1')
SA2 = STA_Q2.add_signal(DA2.position-20, Direction.START_TO_STOP, DA2, label='SA2')
DA_OUT = T.add_detector(position=50, label='DA_OUT')
SA_OUT = T.add_signal(DA_OUT.position-20, Direction.START_TO_STOP, DA_OUT, label='SA_OUT')
for signal in [SA1, SA2, SA_OUT]:
    signal.add_logical_signal("BAL", settings={"Nf": "true"})

STB_Q1 = builder.add_track_section(label='STB_Q1', length=450)
STB_Q2 = builder.add_track_section(label='STB_Q2', length=450)

builder.add_point_switch(T.end(), STB_Q1.begin(), STB_Q2.begin(), label='DVG')
# builder.add_link(T.end(), STB_Q1.begin())


DB_in = T.add_detector(position=T.length-30, label='DB_in')
SB_in = T.add_signal(DB_in.position-20, Direction.START_TO_STOP, DB_in, label='SB_in')

DB1 = STB_Q1.add_detector(position=30, label='DB1')
DB2 = STB_Q2.add_detector(position=30, label='DB2')
SB1 = STB_Q1.add_signal(DB1.position-20, Direction.START_TO_STOP, DB1, label='SB1')
SB2 = STB_Q2.add_signal(DB2.position-20, Direction.START_TO_STOP, DB2, label='SB2')
for signal in [SB1, SB2, SB_in]:
    signal.add_logical_signal("BAL", settings={"Nf": "true"})

station_A = builder.add_operational_point(label="Station_A")
station_A.add_part(STA_Q1, 300)
station_A.add_part(STA_Q2, 300)

station_B = builder.add_operational_point(label="Station_B")
station_B.add_part(STB_Q1, 300)
station_B.add_part(STB_Q2, 300)

infra = builder.build()

builder = SimulationBuilder()

train0 = builder.add_train_schedule(
    Location(STA_Q1, 300),
    Location(STB_Q1, 300),
    label='train0',
    departure_time=0,
    rolling_stock="short_fast_rolling_stock",
)
train1 = builder.add_train_schedule(
    Location(STA_Q2, 300),
    Location(STB_Q2, 300),
    label='train1',
    departure_time=350,
    rolling_stock="short_fast_rolling_stock",
)

sim = builder.build()

infra.save("infra.json")
sim.save('simulation.json')

os.system("java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path infra.json --sim_path simulation.json --res_path results.json")
