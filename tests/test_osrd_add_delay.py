import pytest


def test_osrd_add_delay_first_train(simulation_straight_line):

    simulation_straight_line.reset_delays()
    simulation_straight_line.add_delay(0, 150, 200)
    delayed = simulation_straight_line.delayed()
    assert pytest.approx(
        delayed.last_arrival_times[0]
        - simulation_straight_line.last_arrival_times[0]
    ) == 200.


def test_osrd_add_delay_second_train(simulation_straight_line):

    simulation_straight_line.reset_delays()
    simulation_straight_line.add_delay(1, 150, 200)
    delayed = simulation_straight_line.delayed()
    assert pytest.approx(
        delayed.last_arrival_times[1]
        - simulation_straight_line.last_arrival_times[1]
    ) == 200.


def test_osrd_add_delay_train_label(simulation_straight_line):

    simulation_straight_line.reset_delays()
    simulation_straight_line.add_delay('train0', 150, 200)
    delayed = simulation_straight_line.delayed()
    assert pytest.approx(
        delayed.last_arrival_times[0]
        - simulation_straight_line.last_arrival_times[0]
    ) == 200.


def test_osrd_add_delay_formatted_time(simulation_straight_line):

    simulation_straight_line.reset_delays()
    simulation_straight_line.add_delay(0, '00:02:30', 200)
    delayed = simulation_straight_line.delayed()
    assert pytest.approx(
        delayed.last_arrival_times[0]
        - simulation_straight_line.last_arrival_times[0]
    ) == 200.
