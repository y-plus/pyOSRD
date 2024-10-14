import os
import shutil
from pyosrd import OSRD
from cpagent.cp_agent import CpAgent

os.makedirs('tmp_cases', exist_ok=True)

for case in OSRD.simulations():
    sim=OSRD(simulation=case, dir=os.path.join('tmp_cases', case))
    try:
        sim.folium_map()
    except ZeroDivisionError as e:
        print(case)
        shutil.rmtree(os.path.join('tmp_cases', case), ignore_errors=True)

for case in OSRD.with_delays():
    sim=OSRD(with_delay=case, dir=os.path.join('tmp_cases', case))
    try:
        sim.folium_map()
    except ZeroDivisionError as e:
        print(case)
        shutil.rmtree(os.path.join('tmp_cases', case), ignore_errors=True)

# case='multi_5tr_5st_delay_first'
# sim=OSRD(with_delay=case, dir=os.path.join('tmp_cases', case))
# agent = CpAgent('Delays propagation')
# agent.set_schedules_from_osrd(sim)
# reg = sim.regulate(agent=agent)
