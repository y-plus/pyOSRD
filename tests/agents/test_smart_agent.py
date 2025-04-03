def test_smart_agent_debug(smart_agent_straight_line):
    assert not smart_agent_straight_line.debug 
    assert not smart_agent_straight_line.tree.debug

    smart_agent_straight_line.debug = True
    assert smart_agent_straight_line.debug
    assert smart_agent_straight_line.tree.debug
    
    smart_agent_straight_line.debug = False
    assert not smart_agent_straight_line.debug
    assert not smart_agent_straight_line.tree.debug
    
def test_smart_agent1(smart_agent_straight_line):
    assert not smart_agent_straight_line.dispatched_groot.has_conflicts()
    assert smart_agent_straight_line.tree.best_node == 'SS'

def test_smart_agent2(smart_agent_station_3_tracks):
    assert not smart_agent_station_3_tracks.dispatched_groot.has_conflicts()
    assert smart_agent_station_3_tracks.tree.best_node == 'RS'
