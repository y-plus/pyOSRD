from importlib.resources import files

from .osrd import OSRD

__all__ = [OSRD]

from railjson_generator.schema.simulation.simulation import (
    register_rolling_stocks
)

register_rolling_stocks(files('pyosrd').joinpath('rolling_stocks'))
