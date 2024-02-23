import importlib

from abc import abstractproperty

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pyosrd.schedules import (
    Schedule,
    schedule_from_osrd,
    step_has_fixed_duration,
    weights as weights_
)
from pyosrd.agents import Agent


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
        osrd: OSRD
            OSRD simulation object
        weights: str, optional
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


def compute_metric(
        ref_schedule: Schedule,
        delayed_schedule: Schedule,
        weights: pd.DataFrame) -> float:
    """
    Compute an indicator based on the arrival times of the delayed_schedule compared to the ref_schedule
    ponderated by weights.

    The formula used is as follow (s are all steps of the schedules, a step being a train in a zone):
        sum_s (delayed_arrival - ref_arrival)_s * weight_s

    Parameters
    ----------
    ref_schedule: Schedule
        The reference schedule used as the ideal schedule
    delayed_schedule: Schedule
        The delayed schedule, regulated use to compute the metric
    weights: pd.DataFrame
        the weights use to ponderate all delays
    """ # noqa
    trains = ref_schedule.trains
    starts = ref_schedule.starts
    delayed_starts = delayed_schedule.starts

    metric = 0.

    for train_idx, _ in enumerate(trains):
        for zone in ref_schedule.trajectory(train_idx):
            ref_time = int(starts.loc[zone][train_idx])
            delayed_time = int(delayed_starts.loc[zone][train_idx])
            weight = int(weights.loc[zone][train_idx])

            metric += (delayed_time - ref_time) * weight

    return metric


def regulate_scenario(scenario: str,
                      agent: SchedulerAgent,
                      plot_all=False) -> pd.DataFrame:
    """
    Will regulate the given scenario using the given agent. May plot the infra graph and all the schedules.

    Will return a DataFrame containing the metric for the agent and the given scenario, eg:
                    agent 1
    scenario 1           12

    Parameters
    ----------
    scenario: str
        The scenario to be regulated
    agent: SchedulerAgent
        The agent to be used to regulate the scenario
    plot_all: bool, optional (False by default)
        If set to True all schedules will be displayed (reference, delayed and regulated)
    """ # noqa
    module = importlib.import_module(
                    f".{scenario}",
                    "pyosrd.scenarii"
                )
    function = getattr(module, scenario)
    sim = function()
    delayed_schedule = sim.delayed()

    agent.set_schedules_from_osrd(sim, "all_steps")

    delayed_schedule = schedule_from_osrd(delayed_schedule)
    ref_schedule = schedule_from_osrd(sim)
    regulated_schedule = agent.regulated_schedule
    if plot_all:
        ref_schedule.draw_graph()
        ref_schedule.plot()
        delayed_schedule.plot()
        agent.regulated_schedule.plot()

    data = pd.DataFrame({agent.name:
                         [compute_metric(ref_schedule,
                                         regulated_schedule,
                                         weights_.all_steps(sim))]},
                        index=[scenario])
    return data


def regulate_all_scenarii(
        test_cases: List[str],
        agent: SchedulerAgent
) -> pd.DataFrame:
    """
    Will regulate the given scenarii using the given agent.

    Will return a DataFrame containing the metric for the agent and the given scenarii, eg:
                    agent 1
    scenario 1           12
    scenario 2           16
    scenario 3           22
    scenario 4           33
    scenario 5           98

    Parameters
    ----------
    scenario: List[str]
        The list of scenarii to be regulated
    agent: SchedulerAgent
        The agent to be used to regulate the scenarii
    """ # noqa
    data = []
    for test_case in test_cases:
        data.append(regulate_scenario(test_case, agent))

    return pd.concat(data)


def regulate_all_scenarii_with_all_agents(
        test_cases: List[str],
        agents: List[SchedulerAgent]
) -> pd.DataFrame:
    """
    Will regulate the given scenarii using all the given agent.

    Will return a DataFrame containing the metric for the agents and the given scenarii, eg:
                    agent 1     agent 2     agent 3     agent 4     agent 5
    scenario 1           12         112         212         312       10212
    scenario 2           16         116         216         316       10216
    scenario 3           22         122         222         322       10222
    scenario 4           33         133         233         333       10233
    scenario 5           98         198         298         398       10298

    Parameters
    ----------
    scenario: List[str]
        The list of scenarii to be regulated
    agents: List[SchedulerAgent]
        The agents to be used to regulate the scenario
    """ # noqa
    data = []
    for agent in agents:
        data.append(regulate_all_scenarii(test_cases, agent))
    return pd.concat(data, axis=1)
