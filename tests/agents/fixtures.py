import shutil
from typing import Generator

import pytest

from pyosrd import OSRD
from pyosrd.agents import GDTAgent


@pytest.fixture(scope='session')
def agent_vu_alternate() -> Generator[GDTAgent]:
    sim = OSRD(
        dir='vu_alternate',
        simulation="voie_unique_circulations",
        params_use_case={
            "num_stations":3,
            'num_blocks_between_stations': 6,
            'num_trains': 3,
            'alternate': True,
        })

    yield GDTAgent('groot', sim)
    shutil.rmtree('vu_alternate', ignore_errors=True)
