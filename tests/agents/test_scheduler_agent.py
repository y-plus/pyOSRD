import shutil
import pytest

import pandas as pd
from pandas.testing import assert_frame_equal

from pyosrd import OSRD
from pyosrd.agents.scheduler_agent import SchedulerAgent
from pyosrd.agents.scheduler_agent import regulate_scenarii_with_agents
import pyosrd.schedules.weights as weights


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
        indicator_function = (
            lambda schedule, ref, sim:
            schedule.compute_weighted_delay(ref, weights.all_step(sim))
        )

        DelayTrain0AtDeparture('test').regulate_scenario(
            "foo",
            indicator_function
        )


def test_scheduler_agent_regulate_scenario_delay():
    class DelayTrain0AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[0, 0] = 100.
            return df

    indicator_function = (
        lambda schedule, ref, sim:
        schedule.compute_weighted_delay(ref, weights.all_steps(sim))
    )

    df = DelayTrain0AtDeparture('test').regulate_scenario(
        "c1_delay",
        indicator_function
    )

    assert 440. == df.sum().sum()


def test_scheduler_agent_regulate_scenarii_delay():
    class DelayTrain0AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[0, 0] = 100.
            return df

    indicator_function = (
        lambda schedule, ref, sim:
        schedule.compute_weighted_delay(ref, weights.all_steps(sim))
    )

    df = DelayTrain0AtDeparture('test').regulate_scenarii(
        ["c1_delay", "c1y2_2trains_conflict"],
        indicator_function
    )

    assert 640.0 == df.sum().sum()


def test_scheduler_scenarii_agents_regulate_delay():
    class DelayTrain0AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[0, 0] = 100.
            return df

    class DelayTrain1AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[1, 0] = 50.
            return df

    indicator_function = (
        lambda schedule, ref, sim:
        schedule.compute_weighted_delay(ref, weights.all_steps(sim))
    )

    df = regulate_scenarii_with_agents(
        ["c1_delay", "c1y2_2trains_conflict"],
        [DelayTrain0AtDeparture('test0'), DelayTrain1AtDeparture('test1')],
        indicator_function
    )

    assert 980.0 == df.sum().sum()


def test_scheduler_agent_unknown_instance():

    match = "Unknown scenario foo."
    with pytest.raises(ValueError, match=match):
        regulate_scenarii_with_agents('foo', [], None)
