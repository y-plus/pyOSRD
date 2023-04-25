import rlway.osrd.simulation as sim


def test_simulation_type(simulation_test):
    assert isinstance(simulation_test, dict)


def test_simulation_num_trains(simulation_test):
    assert sim.num_trains(simulation_test) == 2


def test_simulation_departure_times(simulation_test):
    assert sim.departure_times(simulation_test) == [0, 0]
