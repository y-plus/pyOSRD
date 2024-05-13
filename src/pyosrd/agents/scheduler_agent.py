from abc import abstractmethod
import shutil

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pyosrd import OSRD
from pyosrd.schedules import (
    Schedule,
    schedule_from_osrd,
    weights as weights_
)
from pyosrd.agents import Agent


@dataclass
class SchedulerAgent(Agent):
    """Base class for regulation agents that use schedules

    Child classes shoud implement:

    ```python3
    @property
    def regulated_schedule(self) -> Schedule:
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
        Is generated automatically when using set_schedules_from_osrd,
        by default None
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

        self.ref_schedule, self.delayed_schedule =\
            schedule_from_osrd(osrd, delayed=True)
        self.step_has_fixed_duration = (
            self.step_type == 'switch'
            if hasattr(self, 'step_type')
            else self.step_has_fixed_duration
        )
        # self.weights = getattr(weights_, weights)(osrd)
        if weights == 'stations_only':
            self.weights =\
                (self.ref_schedule.step_type == 'station').astype(int)
        elif weights == 'all_steps':
            self.weights = self.ref_schedule.step_type.notna().astype(int)
        else:
            raise ValueError(f"{weights} is not a valid weight identifier")
    @property
    @abstractmethod
    def regulated_schedule(self) -> Schedule:
        ...

    @property
    def steps_extra_delays(self) -> pd.DataFrame:
        return (
            self.regulated_schedule.durations
            - self.delayed_schedule.durations
        ).round(2)

    def regulated(self, osrd):
        self.set_schedules_from_osrd(osrd)
        return super().regulated(osrd)

    def stops(self, osrd) -> list[dict[str, any]]:
        stops = []

        for train in self.steps_extra_delays.columns:

            durations = self.steps_extra_delays[train].replace(0, np.nan)
            non_zero_durations = durations[durations.notna()].to_dict()

            for zone, duration in non_zero_durations.items():
                train_idx = osrd.trains.index(train)
                position = osrd.stop_positions[train_idx][zone]['offset']
                stops.append(
                    {
                        "train": train,
                        "position": position,
                        "duration": duration,
                    }
                )

        return stops

    def load_scenario(
        self,
        scenario: str,
    ) -> None:
        """Load the given scenario.

        Parameters
        ----------
        scenario : str
            The scenario to be regulated
        """

        sim = OSRD(dir="tmp", with_delay=scenario)

        self.set_schedules_from_osrd(sim, "all_steps")

        shutil.rmtree('tmp', ignore_errors=True)

    def regulate_scenario(
        self,
        scenario: str,
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

        sim = OSRD(dir="tmp", with_delay=scenario)

        self.set_schedules_from_osrd(sim, "all_steps")

        df = pd.DataFrame(
            {
                self.name: [
                    self.regulated_schedule.total_weighted_delay(
                        self.ref_schedule,
                        weights_.all_steps(sim),
                    )
                ]
            },
            index=[scenario]
        )

        shutil.rmtree('tmp', ignore_errors=True)

        return df

    def regulate_scenarii(
        self,
        scenarii: list[str]
    ) -> pd.DataFrame:
        """Regulates a list of scenarii using a given agent.

        Parameters
        ----------
        ref_schedule: Schedule
            The reference schedule used as the ideal schedule
        delayed_schedule: Schedule
            The delayed schedule, regulated use to compute the indicator
        Parameters
        ----------
        scenarii : list[str]
            The list of scenarii to be regulated
        agent : SchedulerAgent
            The agent to be used to regulate the scenarii

        Returns
        -------
        pd.DataFrame
            DataFrame containing the indicator for the agent
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
        DataFrame containing the indicator for the agents
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
        scenarii = OSRD.with_delays()
    elif scenarii in OSRD.with_delays():
        scenarii = [scenarii]
    elif isinstance(scenarii, str):
        raise ValueError(f"Unknown scenario {scenarii}.")

    for scenario in scenarii:
        if scenario not in OSRD.with_delays():
            raise ValueError(
                f"{scenario} is not a valid scenario."
            )

    if isinstance(agents, SchedulerAgent):
        agents = [agents]

    data = [
        agent.regulate_scenarii(scenarii)
        for agent in agents
    ]
    return pd.concat(data, axis=1)
