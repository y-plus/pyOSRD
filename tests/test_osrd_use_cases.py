import shutil

import pytest

from pyosrd import OSRD


@pytest.mark.parametrize('simulation', OSRD.simulations)
def test_use_cases_no_fail(simulation):
    try:
        OSRD(simulation=simulation, dir='tmp')
    except ValueError:
        assert False
    shutil.rmtree('tmp')


def test_use_cases_unknown_case():
    match = "unknown is not a valid use case simulation name."
    with pytest.raises(ValueError, match=match):
        OSRD(simulation='unknown')
