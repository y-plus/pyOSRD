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

STA_Q1 = builder.add_track_section(label='STA_Q1', length=450)
STA_Q2 = builder.add_track_section(label='STA_Q2', length=450)

T = builder.add_track_section(label='T', length=10_000.)

builder.add_point_switch(T.begin(), STA_Q1.end(), STA_Q2.end(), label='CVG')


DA1 = STA_Q1.add_detector(position=430, label='DA1')
DA2 = STA_Q2.add_detector(position=430, label='DA2')
SA1 = STA_Q1.add_signal(DA1.position-20, Direction.START_TO_STOP, DA1)
SA2 = STA_Q2.add_signal(DA2.position-20, Direction.START_TO_STOP, DA2)
DA_out = T.add_detector(position=50, label='DA_out')
SA_OUT = T.add_signal(DA_out.position-20, Direction.START_TO_STOP, DA_out)

STB_Q1 = builder.add_track_section(label='STB_Q1', length=450)
STB_Q2 = builder.add_track_section(label='STB_Q2', length=450)

builder.add_point_switch(T.end(), STB_Q1.begin(), STB_Q2.begin(), label='DVG')

DB_in = T.add_detector(position=T.length-30, label='DB_in')
DB1 = STB_Q1.add_detector(position=30, label='DB1')
DB2 = STB_Q2.add_detector(position=30, label='DB2')
SB_in = T.add_signal(DB_in.position-20, Direction.START_TO_STOP, DB_in)
SB1 = STB_Q1.add_signal(DB1.position-20, Direction.START_TO_STOP, DB1)
SB2 = STB_Q2.add_signal(DB2.position-20, Direction.START_TO_STOP, DB2)

STA_Q1.add_buffer_stop(position=0, applicable_direction=ApplicableDirection.START_TO_STOP)
STA_Q2.add_buffer_stop(position=0, applicable_direction=ApplicableDirection.START_TO_STOP)
STB_Q1.add_buffer_stop(position=STB_Q1.length, applicable_direction=ApplicableDirection.START_TO_STOP)
STB_Q2.add_buffer_stop(position=STB_Q2.length, applicable_direction=ApplicableDirection.START_TO_STOP)

D, S = [], []
for pos in range(4):
    D.append(T.add_detector(position = 2000.*(1+pos), label=f"D{str(pos)}"))
    T.add_signal(D[pos].position-20, Direction.START_TO_STOP, D[pos])

infra = builder.build()


builder = SimulationBuilder(infra)

train0 = builder.add_train_schedule(
    Location(STA_Q1, 400),
    Location(STB_Q1, 440),
    label='train0',
    departure_time=0,
    # rolling_stock="short_fast_rolling_stock",
)
train0.add_stop(100, location=Location(T, 4500))


# train1 = builder.add_train_schedule(
#     Location(STA_Q2, 400),
#     Location(STB_Q2, 440),
#     label='train1',
#     departure_time=60,
#     # rolling_stock="short_fast_rolling_stock"
# )

sim = builder.build()


infra.save("infra.json")
sim.save('simulation.json')
os.system("java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path infra.json --sim_path simulation.json --res_path results.json")