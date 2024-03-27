import pytest


def test_add_train(modify_sim):
    modify_sim.add_train(
        label='new_train',
        locations=[('T0', 300), ('T4', 490)],
        departure_time=400
    )
    modify_sim.run()
    assert modify_sim.trains == ['train0', 'train1', 'new_train']


def test_add_train_existing_label(modify_sim):
    with pytest.raises(ValueError):
        modify_sim.add_train(
            label='train0',
            locations=[('T0', 300), ('T4', 490)],
            departure_time=400
        )


def test_cancel_train_by_label(modify_sim):
    modify_sim.cancel_train('train0')
    modify_sim.run()
    assert modify_sim.trains == ['train1']


def test_cancel_train_by_index(modify_sim):
    modify_sim.cancel_train(0)
    modify_sim.run()
    assert modify_sim.trains == ['train1']


def test_cancel_all_trains(modify_sim):
    modify_sim.cancel_all_trains()
    modify_sim.run()
    assert modify_sim.trains == []


def test_stop_train_by_label(modify_sim):
    arrival_time = \
        modify_sim.points_encountered_by_train(0)[-1]['t_base']
    modify_sim.stop_train(
        'train0',
        position=300,
        duration=60.
    )
    modify_sim.run()
    new_arr_time = \
        modify_sim.points_encountered_by_train(0)[-1]['t_base']
    assert new_arr_time > arrival_time


def test_stop_train_by_id(modify_sim):
    arrival_time = \
        modify_sim.points_encountered_by_train(0)[-1]['t_base']
    modify_sim.stop_train(
        0,
        position=300,
        duration=60.
    )
    modify_sim.run()
    new_arr_time = \
        modify_sim.points_encountered_by_train(0)[-1]['t_base']
    assert new_arr_time > arrival_time


def test_copy_train_by_id(modify_sim):
    modify_sim.copy_train(0, 'new_train', 100.)
    modify_sim.run()

    assert 'new_train' in modify_sim.trains


def test_copy_train_by_label(modify_sim):
    modify_sim.copy_train('train0', 'new_train', 100.)
    modify_sim.run()

    assert 'new_train' in modify_sim.trains


def test_copy_train_already_existing_label(modify_sim):
    match = "'train1' is already used as a train label"
    with pytest.raises(ValueError, match=match):
        modify_sim.copy_train(
            train='train0',
            new_train_label='train1',
            departure_time=60.,
        )
