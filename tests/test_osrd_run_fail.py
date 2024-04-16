import shutil

import pytest

from pyosrd import OSRD


def test_run_shoud_fail_and_raise_exception_with_malformed_jsons():
    sim = OSRD(dir='tmp4', )
    sim.infra, sim.simulation = '', ''
    with pytest.raises(RuntimeError):
        sim.run()
    shutil.rmtree('tmp4', ignore_errors=True)
