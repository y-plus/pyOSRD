import importlib

from abc import abstractproperty

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pyosrd import OSRD
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
    ref_schedule: Schedule | None, optional
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

    ref_schedule: Schedule | None = None
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

        self.ref_schedule = schedule_from_osrd(osrd)
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

    def regulate_scenario(
        self,
        scenario: str,
        plot_all=False
    ) -> pd.DataFrame:
        """Regulates the given scenario using the given agent.

        Parameters
        ----------
        scenario : str
            The scenario to be regulated
        plot_all : bool, optional
             If True, all schedules will be displayed (reference,
            delayed and regulated), by default False

        Returns
        -------
        pd.DataFrame
            DataFrame containing the indictor value for
            the agent and the given scenario, eg:
                            agent 1
            scenario 1           12

        Raises
        ------
        ValueError
            When the scenario is unknown
        """

        if scenario not in OSRD.scenarii:
            raise ValueError(
                f"{scenario} is not a valid scenario."
            )

        module = importlib.import_module(
            f".{scenario}",
            "pyosrd.scenarii"
        )
        function = getattr(module, scenario)
        sim = function()
        delayed_schedule = sim.delayed()

        self.set_schedules_from_osrd(sim, "all_steps")

        delayed_schedule = schedule_from_osrd(delayed_schedule)
        ref_schedule = schedule_from_osrd(sim)
        regulated_schedule = self.regulated_schedule

        if plot_all:
            ref_schedule.draw_graph()
            ref_schedule.plot()
            delayed_schedule.plot()
            self.regulated_schedule.plot()

        return pd.DataFrame(
            {
                self.name: [
                    regulated_schedule.compute_weighted_delays(
                        ref_schedule,
                        weights_.all_steps(sim),
                    )
                ]
            },
            index=[scenario]
        )

    def regulate_scenarii(
        self,
        scenarii: list[str]
    ) -> pd.DataFrame:
        """Regulates a list of scenarii using a given agent.

        Parameters
        ----------
        scenarii : list[str]
            The list of scenarii to be regulated
        agent : SchedulerAgent
            The agent to be used to regulate the scenarii

        Returns
        -------
        pd.DataFrame
            DataFrame containing the metric for the agent
            and the given scenarii, eg:
                            agent 1
            scenario 1           12
            scenario 2           16
            scenario 3           22
            scenario 4           33
            scenario 5           98
        """

        data = [
            self.regulate_scenario(scenario)
            for scenario in scenarii
        ]
        return pd.concat(data)


def regulate_scenarii_with_agents(
        scenarii: str | list[str],
        agents: SchedulerAgent | list[SchedulerAgent]
) -> pd.DataFrame:
    """Regulates a list of scenarii using a list of agents"

    Parameters
    ----------
    scenarii : str | list[str]
         The list of scenarii to be regulated. Ccan also be "all"
         to start all scenarii or directly the name of one scenario
    agents : SchedulerAgent | list[SchedulerAgent]
        The agents to be used to regulate the scenarii. Can  be
        a single agent or a list of agents.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the metric for the agents
        and the given scenarii, eg:
                        agent 1     agent 2     agent 3     agent 4     agent 5
        scenario 1           12         112         212         312       10212
        scenario 2           16         116         216         316       10216
        scenario 3           22         122         222         322       10222
        scenario 4           33         133         233         333       10233
        scenario 5           98         198         298         398       10298


    Raises
    ------
    ValueError
        When a scenario is unknown
    """

    if scenarii == 'all':
        scenarii = OSRD.scenarii
    elif scenarii in OSRD.scenarii:
        scenarii = [scenarii]
    elif isinstance(scenarii, str):
        raise ValueError(f"Unknown scenario {scenarii}")

    if isinstance(agents, SchedulerAgent):
        agents = [agents]

    data = [
        agent.regulate_scenarii(scenarii)
        for agent in agents
    ]
    return pd.concat(data, axis=1)
