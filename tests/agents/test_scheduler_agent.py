import shutil

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest


from pyosrd import OSRD
from pyosrd.agents.scheduler_agent import SchedulerAgent
from pyosrd.agents.scheduler_agent import regulate_scenarii_with_agents


@pytest.fixture(scope='session')
def test_agent() -> SchedulerAgent:
    class DelayTrain0AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[0, 0] = 100.
            return df

    return DelayTrain0AtDeparture('test')


@pytest.fixture(scope='session')
def test_agent2() -> SchedulerAgent:
    class DelayTrain1AtDeparture(SchedulerAgent):
        @property
        def steps_extra_delays(self) -> pd.DataFrame:
            df = self.ref_schedule.durations * 0.
            df.iloc[1, 0] = 50.
            return df

    return DelayTrain1AtDeparture('test2')


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


def test_scheduler_agent_in_regulate(test_agent):

    sim = OSRD(simulation='station_capacity2', dir='tmp2')
    sim.add_delay('train0', time_threshold=90, delay=280.)
    delayed = sim.delayed()

    regulated = sim.regulate(agent=test_agent)

    arrival_times = [
        s.points_encountered_by_train(0)[-1]['t_base']
        for s in (sim, delayed, regulated)
    ]

    assert arrival_times == sorted(arrival_times)
    shutil.rmtree('tmp2', ignore_errors=True)


def test_scheduler_agent_regulate_scenario_error(test_agent):

    match = "foo is not a valid use case with_delay name."
    with pytest.raises(ValueError, match=match):
        test_agent.regulate_scenario(
            "foo"
        )


def test_scheduler_agent_regulate_scenario_delay(test_agent):

    df = test_agent.regulate_scenario("c1_2trains_delay_train1")

    assert abs(440.0 - df.sum().sum()) < 1e-3


def test_scheduler_agent_regulate_scenarii_delay(test_agent):

    df = test_agent.regulate_scenarii(
        ["c1_2trains_delay_train1", "c1y2_2trains_conflict"]
    )

    assert abs(640 - df.sum().sum()) < 1e-3


def test_scheduler_scenarii_agents_regulate_delay(test_agent, test_agent2):

    df = regulate_scenarii_with_agents(
        ["c1_2trains_delay_train1", "c1y2_2trains_conflict"],
        [test_agent, test_agent2]
    )

    assert abs(980 - df.sum().sum()) < 1e-3


def test_scheduler_scenarii_one_agent_regulate_delay(test_agent):

    df = regulate_scenarii_with_agents(
        "c1_2trains_delay_train1",
        test_agent
    )

    assert abs(440.0 - df.sum().sum()) < 1e-3


def test_scheduler_agent_unknown_instance():

    match = "Unknown scenario foo."
    with pytest.raises(ValueError, match=match):
        regulate_scenarii_with_agents('foo', [])


def test_scheduler_agent_unknown_instances():

    match = "foo is not a valid scenario."
    with pytest.raises(ValueError, match=match):
        regulate_scenarii_with_agents(['foo', 'bar'], [])


def test_scheduler_agent_load_instance(test_agent):
    try:
        test_agent.load_scenario('c1_2trains_delay_train1')
    except ValueError:
        assert False


def test_scheduler_agent_load_unknown_instance(test_agent):

    match = "foo is not a valid use case with_delay name."
    with pytest.raises(ValueError, match=match):
        test_agent.load_scenario('foo')
