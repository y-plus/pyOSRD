import importlib
from importlib.resources import files
import json
from .osrd import OSRD


__all__ = [OSRD]


ROLLING_STOCKS = {}


for path in files('pyosrd').joinpath('rolling_stocks/').iterdir():
    if path.suffix == '.json':
        with open(path) as f:
            rs = json.load(f)
            ROLLING_STOCKS[rs["name"]] = rs


importlib.import_module(
    'railjson_generator.schema.simulation.simulation'
).ROLLING_STOCKS = ROLLING_STOCKS
