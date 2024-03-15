import shutil
import pytest

import pandas as pd
from pandas.testing import assert_frame_equal

from pyosrd import OSRD
from pyosrd.agents.scheduler_agent import SchedulerAgent


def test_scheduler_agent_autonomous(two_trains):

    class DummySchedulerAgent(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            return self.ref_schedule.durations * 0.

    agent = DummySchedulerAgent(
        'dummy',
        ref_schedule=two_trains,
        delayed_schedule=two_trains.add_delay(0, 0, 10),
        step_has_fixed_duration=two_trains.durations.replace(1, False),
    )

    assert agent.ref_schedule == two_trains
    assert_frame_equal(
        agent.delayed_schedule.df,
        two_trains.add_delay(0, 0, 10).df
    )
    assert agent.step_has_fixed_duration.sum().sum() == 0
    assert_frame_equal(
        agent.regulated_schedule.df,
        two_trains.add_delay(0, 0, 10).df
    )


def test_scheduler_agent_in_regulate():

    sim = OSRD(use_case='station_capacity2', dir='tmp2')
    sim.add_delay('train0', time_threshold=90, delay=280.)
    delayed = sim.delayed()

    class DelayTrain0AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[0, 0] = 100.
            return df

    regulated = sim.regulate(agent=DelayTrain0AtDeparture('test'))

    arrival_times = [
        s.points_encountered_by_train(0)[-1]['t_base']
        for s in (sim, delayed, regulated)
    ]

    assert arrival_times == sorted(arrival_times)
    shutil.rmtree('tmp2', ignore_errors=True)


def test_scheduler_agent_regulate_scenario_error():
    class DelayTrain0AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[0, 0] = 100.
            return df

    match = "foo is not a valid scenario."
    with pytest.raises(ValueError, match=match):
        DelayTrain0AtDeparture('test').regulate_scenario("foo")
