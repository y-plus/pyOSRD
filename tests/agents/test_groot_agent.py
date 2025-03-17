import os

from pyosrd.agents import load_agent

def test_groot_agent_save_load(agent_vu_alternate) -> None:
    agent_vu_alternate.save('tmp_agent.pkl')

    assert os.path.isfile('tmp_agent.pkl')

    agent2 = load_agent('tmp_agent.pkl')

    for k in agent_vu_alternate.__dict__:
        assert agent2.__dict__[k] == agent_vu_alternate.__dict__[k]

    os.remove('tmp_agent.pkl')
