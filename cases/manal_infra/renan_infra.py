import os
# import rlway.pyosrd

from railjson_generator import (
    InfraBuilder,
    SimulationBuilder,
    ApplicableDirection,
    Location,
)

from railjson_generator.schema.infra.direction import Direction
from railjson_generator.schema.simulation.stop import Stop
from railjson_generator import get_output_dir

from typing import Mapping, Tuple

# OUTPUT_DIR = get_output_dir()
OUTPUT_DIR = '.'

def add_signal_on_ports(switch, ports: Mapping[str, Tuple[str, str]]):
    """Add signals and detectors to given ports.
    Args:
        ports: A dictionary of port names to (detector_label, signal_label) pairs.
    """
    # Reference distances, in meters
    # SIGNAL_TO_SWITCH = 200
    # DETECTOR_TO_SWITCH = 180
    SIGNAL_TO_SWITCH = 40
    DETECTOR_TO_SWITCH = 20

    for port, (det_label, sig_label) in ports.items():
        detector = switch.add_detector_on_port(port, DETECTOR_TO_SWITCH, label=det_label)
        signal = switch.add_signal_on_port(port, SIGNAL_TO_SWITCH, label=sig_label, linked_detector=detector)
        signal.add_logical_signal(signaling_system="BAL", settings={"Nf": "true"})

builder = InfraBuilder()

# ================================
#  Create track sections
# ================================

t0 = builder.add_track_section(length=450, label="STA_Q1", track_name="V1", track_number=1)
t1 = builder.add_track_section(length=450, label="STA_Q2", track_name="V2", track_number=1)
t2 = builder.add_track_section(length=450, label="STB_Q1", track_name="V3", track_number=1)
t3 = builder.add_track_section(length=450, label="STB_Q2", track_name="V4", track_number=1)
t4 = builder.add_track_section(length=10000, label='T',    track_name="V5", track_number=1)

# =============================================
#  Create switches (with signals & detectors)
# =============================================

CVG = builder.add_point_switch(
    label="CVG",
    base=t4.begin(),
    left=t0.end(),
    right=t1.end(),
)
add_signal_on_ports(CVG,{
                        "base": ("DA_out", "S0"),
                        "right": ("DA1", "S1"),
                        "left": ("DA2", "S2")
                    })

DVG = builder.add_point_switch(
    label="DVG",
    base=t4.end(),
    left=t2.begin(),
    right=t3.begin(),
)
add_signal_on_ports(DVG,{
                        "base": ("DB_in", "S3"),
                        "left": ("DB1", "S4"),
                        "right": ("DB2", "S5"),
                    })

# =============================================
#  Add stations
# =============================================

station_A = builder.add_operational_point(label="Station_A")
station_A.add_part(t0, 300)
station_A.add_part(t1, 300)

station_B = builder.add_operational_point(label="Station_B")
station_B.add_part(t2, 300)
station_B.add_part(t3, 300)


# ================================
# Produce the railjson
# ================================

# Build infra
infra = builder.build()

# Save railjson
infra.save("infra.json")

# ================================
# Produce the simulation file
# ================================

builder = SimulationBuilder()

train_0 = builder.add_train_schedule(
    Location(t0, 300),
    Location(t2, 300),
    label="train.0",
    departure_time=0
)


train_1 = builder.add_train_schedule(
    Location(t1, 300),
    Location(t3, 300),
    label="train.1",
    departure_time=60
)

# Build simulation
sim = builder.build()

# Save railjson
sim.save("simulation.json")

os.system("java -jar /home/renan/osrd/core/build/libs/osrd-all.jar standalone-simulation --infra_path infra.json --sim_path simulation.json --res_path results.json")
