import os

from pyosrd.agents import load_agent
from .fixtures import Agent


def test_base_agent_name(base_agent_straight_line: Agent):
    assert base_agent_straight_line.name == "base_agent"


def test_base_agent_debug(base_agent_straight_line: Agent):
    assert not base_agent_straight_line.debug 
    assert not base_agent_straight_line.debug 
    base_agent_straight_line.debug = True
    assert base_agent_straight_line.debug


def test_base_agent_add_delay_and_reset(base_agent_straight_line: Agent):
    assert base_agent_straight_line.ref_groot == base_agent_straight_line.disrupted_groot
    base_agent_straight_line.add_delay('train00', 'A/V1', 200)

    assert base_agent_straight_line.ref_groot.times['train00'] != base_agent_straight_line.disrupted_groot.times['train00']
    assert base_agent_straight_line.ref_groot.times['train01'] == base_agent_straight_line.disrupted_groot.times['train01']

    base_agent_straight_line.reset_disruptions()
    assert base_agent_straight_line.ref_groot == base_agent_straight_line.disrupted_groot


def test_groot_agent_save_load(base_agent_straight_line: Agent) -> None:
    base_agent_straight_line.save('tmp_agent.pkl')
    assert os.path.isfile('tmp_agent.pkl')

    agent2 = load_agent('tmp_agent.pkl')
    for k in base_agent_straight_line.__dict__:
        assert agent2.__dict__[k] == base_agent_straight_line.__dict__[k]

    os.remove('tmp_agent.pkl')
