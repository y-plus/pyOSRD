import shutil

import pytest

from pyosrd import OSRD
from pyosrd.agents.base_agent import BaseAgent
from pyosrd.agents import SmartAgent

class Agent(BaseAgent):

    def _calculate_dispatch(self, debug):
        ...

    def _calculate_interlocking(self, debug):
        ...


@pytest.fixture(scope='session')
def base_agent() -> Agent:
    sim = OSRD(
        dir='tmp',
        simulation="c1_with_blocks_3trains"
    )
    agent = Agent("base_agent", sim)
    shutil.rmtree('tmp', ignore_errors=True)
    return agent


@pytest.fixture(scope='session')
def smart_agent_straight_line() -> SmartAgent:
    sim = OSRD(
        dir='tmp',
        simulation="c1_with_blocks_3trains"
    )
    agent = SmartAgent("base_agent", sim)
    agent.add_delay('train00', 'A/V1', 100)
    shutil.rmtree('tmp', ignore_errors=True)
    return agent


@pytest.fixture(scope='session')
def smart_agent_station_3_tracks() -> SmartAgent:
    sim = OSRD(
        dir='tmp_3tracks',
        simulation="c1yy3yy1_3trains"
    )
    agent = SmartAgent("base_agent", sim)
    agent.add_delay('train0', 'station/T2', 120)
    shutil.rmtree('tmp_3tracks', ignore_errors=True)
    return agent
