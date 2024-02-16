import os
import shutil

import folium

from pyosrd import OSRD


def test_map():
    os.makedirs('small_infra', exist_ok=True)
    os.system('python doc/tutorials/small_infra.py small_infra')

    sim = OSRD('small_infra')
    m = sim.folium_map()
    assert isinstance(m, folium.Map)

    shutil.rmtree('small_infra', ignore_errors=True)
