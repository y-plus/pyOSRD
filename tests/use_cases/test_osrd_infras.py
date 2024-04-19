import shutil

import pytest

from pyosrd import OSRD


@pytest.mark.parametrize('infra', OSRD.infras())
def test_infras_no_fail(infra):
    try:
        OSRD(dir="tmp_infra", infra=infra)
    except ValueError:
        assert False
    shutil.rmtree('tmp_infra')
