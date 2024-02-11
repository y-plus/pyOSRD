import shutil

import pytest

from pyosrd import OSRD


@pytest.mark.parametrize('use_case', OSRD.use_cases)
def test_use_cases_no_fail(use_case):
    try:
        OSRD(use_case=use_case, dir='tmp')
    except ValueError:
        assert False
    shutil.rmtree('tmp')


def test_use_cases_unknown_case():
    match = "unknown is not a valid use case name."
    with pytest.raises(ValueError, match=match):
        OSRD(use_case='unknown')
