import sys
sys.path.append('../../')

from rlway.pyosrd import OSRD
from tests._build_case_two_lanes import infra_two_lanes, simulation_two_lanes_two_trains

built_infra = infra_two_lanes()
built_simulation = simulation_two_lanes_two_trains(built_infra)

built_infra.save('infra.json')
built_simulation.save('simulation.json')

two_lanes = OSRD()
two_lanes.run()
