import shutil

import pytest

from pyosrd import OSRD


@pytest.mark.parametrize('with_delay', OSRD.with_delays)
def test_with_delays_no_fail(with_delay):
    try:
        sim = OSRD(dir="tmp", with_delay=with_delay)
        sim.delayed()
    except ValueError:
        assert False
    shutil.rmtree('tmp')
