import os

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    Location,
)
from railjson_generator.schema.infra.direction import Direction

builder = InfraBuilder()

STA_Q1 = builder.add_track_section(label='STA_Q1', length=450)
T = builder.add_track_section(label='T', length=10_000.)
builder.add_link(STA_Q1.end(), T.begin())

DA_out = T.add_detector(position=50, label='DA_out')
SA_OUT = T.add_signal(DA_out.position-20, Direction.START_TO_STOP, DA_out)
SA_OUT.add_logical_signal("BAL", settings={"Nf": "false"})

STB_Q1 = builder.add_track_section(label='STB_Q1', length=450)
builder.add_link(T.end(), STB_Q1.begin())

DB_in = T.add_detector(position=T.length-30, label='DB_in')
SB_in = T.add_signal(DB_in.position-20, Direction.START_TO_STOP, DB_in)
SB_in.add_logical_signal("BAL", settings={"Nf": "false"})

infra = builder.build()

builder = SimulationBuilder(infra)

train0 = builder.add_train_schedule(
    Location(STA_Q1, 300),
    Location(STB_Q1, 300),
    label='train0',
    departure_time=0
)

sim = builder.build()

infra.save("infra.json")

sim.save('simulation.json')

os.system("java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path infra.json --sim_path simulation.json --res_path results.json")
