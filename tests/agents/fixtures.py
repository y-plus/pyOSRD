import shutil

import pytest

from pyosrd import OSRD
from pyosrd.agents.base_agent import BaseAgent


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
