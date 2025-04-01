import os

from pyosrd.agents import load_agent
from .fixtures import Agent


def test_base_agent_name(base_agent: Agent):
    assert base_agent.name == "base_agent"


def test_base_agent_debug(base_agent: Agent):
    assert not base_agent.debug 
    base_agent.debug = True
    assert base_agent.debug


def test_base_agent_add_delay_and_reset(base_agent: Agent):
    assert base_agent.ref_groot == base_agent.disrupted_groot
    base_agent.add_delay('train00', 'A/V1', 200)

    assert base_agent.ref_groot.times['train00'] != base_agent.disrupted_groot.times['train00']
    assert base_agent.ref_groot.times['train01'] == base_agent.disrupted_groot.times['train01']

    base_agent.reset_disruptions()
    assert base_agent.ref_groot == base_agent.disrupted_groot


def test_groot_agent_save_load(base_agent: Agent) -> None:
    base_agent.save('tmp_agent.pkl')
    assert os.path.isfile('tmp_agent.pkl')

    agent2 = load_agent('tmp_agent.pkl')
    for k in base_agent.__dict__:
        assert agent2.__dict__[k] == base_agent.__dict__[k]

    os.remove('tmp_agent.pkl')
