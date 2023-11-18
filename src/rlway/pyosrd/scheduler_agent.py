from abc import abstractproperty

from dataclasses import dataclass

import numpy as np
import pandas as pd

from rlway.schedules import (
    Schedule,
    schedule_from_osrd,
    step_has_fixed_duration,
    weights as weights_
)
from rlway.pyosrd.agents import Agent


@dataclass
class SchedulerAgent(Agent):
    """Base class for regulation agents that use schedules

    Child classes shoud implement:

    ```python3
    @property
    def steps_extra_delays(self) -> pd.DataFrame:
        ...
    ```

    Attributes
    ----------
    name: str
        Inherited from abstract base class Agent
    initial_schedule: Schedule | None, optional
        Schedule for initial undelyed simulation, by default None
    delayed_schedule: Schedule | None, optional
        Schedule for delayed simulation, by default None
    step_has_fixed_duration: pd.DataFrame | None, optional
        DataFrame of booleans indicating if the steps duration can be modified.
        Can be generated using the function with the same name
        from subpackage schedules, by default None
    weights: pd.DataFrame | None, optional
        DataFrame of step weights for the weighted total delay.
        Can be generated using methods from the schedules.weight module
        , by default None

    """

    initial_schedule: Schedule | None = None
    delayed_schedule: Schedule | None = None
    step_has_fixed_duration: pd.DataFrame | None = None
    weights: pd.DataFrame | None = None

    def set_schedules_from_osrd(
        self,
        osrd,
        weights: str = 'stations_only'
    ) -> None:
        """Set schedules and infos from an OSRD object

        Parameters
        ----------
        osrd : OSRD
            OSRD simulation object
        weights : str, optional
            Weights initialization, either 'all_steps" or "stations_only',
            by default 'stations_only'
        """

        self.initial_schedule = schedule_from_osrd(osrd)
        self.delayed_schedule = schedule_from_osrd(osrd.delayed())
        self.step_has_fixed_duration = \
            step_has_fixed_duration(osrd)
        self.weights = getattr(weights_, weights)(osrd)

    @abstractproperty
    def steps_extra_delays(self) -> pd.DataFrame:
        pass

    def regulated(self, osrd):
        self.set_schedules_from_osrd(osrd)
        return super().regulated(osrd)

    def stops(self, osrd) -> list[dict[str, any]]:
        stops = []

        for train in self.steps_extra_delays.columns:

            durations = self.steps_extra_delays[train].replace(0, np.nan)
            non_zero_durations = durations[durations.notna()].to_dict()

            for zone, duration in non_zero_durations.items():
                position = osrd.stop_positions[train][zone]['offset']
                stops.append(
                    {
                        "train": train,
                        "position": position,
                        "duration": duration,
                    }
                )

        return stops

    @property
    def regulated_schedule(self) -> Schedule:

        regulated_schedule = self.delayed_schedule

        for train in self.steps_extra_delays.columns:
            delays = self.steps_extra_delays[train].replace(0, np.nan)
            for zone, delay in delays[delays.notna()].to_dict().items():
                regulated_schedule = \
                    regulated_schedule.add_delay(train, zone, delay)

        return regulated_schedule
