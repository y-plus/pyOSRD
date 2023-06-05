import shutil

import pytest

from rlway.pyosrd import OSRD


def test_use_cases_no_fail():
    for use_case in OSRD.use_cases:
        try:
            OSRD(use_case=use_case, dir='tmp')
        except ValueError:
            assert False
    shutil.rmtree('tmp')


def test_use_cases_unknown_case():
    match = "unknown is not a valid use case name."
    with pytest.raises(ValueError, match=match):
        OSRD(use_case='unknown')
