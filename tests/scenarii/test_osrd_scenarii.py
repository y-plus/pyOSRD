import importlib
import shutil

import pytest

from pyosrd import OSRD


@pytest.mark.parametrize('scenario', OSRD.scenarii)
def test_use_scenarii_no_fail(scenario):
    try:
        module = importlib.import_module(
            f".{scenario}",
            "pyosrd.scenarii"
        )
        function = getattr(module, scenario)
        sim = function()
        sim.delayed()
    except ValueError:
        assert False
    shutil.rmtree('tmp')
