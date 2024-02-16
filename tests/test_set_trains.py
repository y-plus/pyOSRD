import pytest


def test_add_train(use_case_set_trains):
    use_case_set_trains.add_train(
        label='new_train',
        locations=[('T0', 300), ('T4', 490)],
        departure_time=400
    )
    use_case_set_trains.run()
    assert use_case_set_trains.trains == ['train0', 'train1', 'new_train']


def test_add_train_existing_label(use_case_set_trains):
    with pytest.raises(ValueError):
        use_case_set_trains.add_train(
            label='train0',
            locations=[('T0', 300), ('T4', 490)],
            departure_time=400
        )


def test_cancel_train_by_label(use_case_set_trains):
    use_case_set_trains.cancel_train('train0')
    use_case_set_trains.run()
    assert use_case_set_trains.trains == ['train1']


def test_cancel_train_by_index(use_case_set_trains):
    use_case_set_trains.cancel_train(0)
    use_case_set_trains.run()
    assert use_case_set_trains.trains == ['train1']


def test_cancel_all_trains(use_case_set_trains):
    use_case_set_trains.cancel_all_trains()
    use_case_set_trains.run()
    assert use_case_set_trains.trains == []


def test_stop_train_by_label(use_case_set_trains):
    arrival_time = \
        use_case_set_trains.points_encountered_by_train(0)[-1]['t_base']
    use_case_set_trains.stop_train(
        'train0',
        position=300,
        duration=60.
    )
    use_case_set_trains.run()
    new_arr_time = \
        use_case_set_trains.points_encountered_by_train(0)[-1]['t_base']
    assert new_arr_time > arrival_time


def test_stop_train_by_id(use_case_set_trains):
    arrival_time = \
        use_case_set_trains.points_encountered_by_train(0)[-1]['t_base']
    use_case_set_trains.stop_train(
        0,
        position=300,
        duration=60.
    )
    use_case_set_trains.run()
    new_arr_time = \
        use_case_set_trains.points_encountered_by_train(0)[-1]['t_base']
    assert new_arr_time > arrival_time


def test_copy_train_by_id(use_case_set_trains):
    use_case_set_trains.copy_train(0, 'new_train', 100.)
    use_case_set_trains.run()

    assert 'new_train' in use_case_set_trains.trains


def test_copy_train_by_label(use_case_set_trains):
    use_case_set_trains.copy_train('train0', 'new_train', 100.)
    use_case_set_trains.run()

    assert 'new_train' in use_case_set_trains.trains


def test_copy_train_already_existing_label(use_case_set_trains):
    match = "'train1' is already used as a train label"
    with pytest.raises(ValueError, match=match):
        use_case_set_trains.copy_train(
            train='train0',
            new_train_label='train1',
            departure_time=60.,
        )
