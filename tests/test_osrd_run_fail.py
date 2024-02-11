import pytest

from rlway import OSRD


def test_run_shoud_fail_and_raise_exception_with_malformed_jsons():
    sim = OSRD(dir='.', )
    sim.infra, sim.simulation = '', ''
    with pytest.raises(RuntimeError):
        sim.run()
