import os

from pyosrd.agents import GDTAgent

def test_groot_agent_save_load(agent_vu_alternate) -> None:
    agent_vu_alternate.save('agent.pkl')

    assert os.path.isfile('agent.pkl')

    agent2 = GDTAgent.load('agent.pkl')

    for k in agent_vu_alternate.__dict__:
        assert agent2.__dict__[k] == agent_vu_alternate.__dict__[k]

    os.remove('agent.pkl')
