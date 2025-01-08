class TestsOneTrain:
    
    def test_groot_speedup_1train_1(self, groot_1train):
        delay = 1
        disrupted = groot_1train.add_delay('train1', 'A', delay)
        reaccelerated = disrupted.speedup(ref=groot_1train, train='train1', zone='B')
        expected_times = {
            'A': (1, 4),
            'B': (3.5, 5.5),
            'C': (5.0, 8.0)
        }
        assert reaccelerated.times['train1'] == expected_times


    def test_groot_speedup_1train_2(self, groot_1train):
        delay = 2
        disrupted = groot_1train.add_delay('train1', 'A', delay)
        reaccelerated = disrupted.speedup(ref=groot_1train, train='train1', zone='B')
        expected_times = {
            'A': (2, 5),
            'B': (4.5, 6.5),
            'C': (6.0, 8.0)
        }
        assert reaccelerated.times['train1'] == expected_times


class TestsTwoTrains:

    def test_groot_speedup_2trains(self, groot_2trains):
        disrupted = groot_2trains.add_delay('train1', 'A', 2)
        dispatched = disrupted.add_delay('train2', 'A', 1)
        reaccelerated = dispatched.speedup(groot_2trains, 'train2', 'B')
        expected_times = {
            'A': (5, 8),
            'B': (7.5, 10.5),
            'C': (10, 12)
        }
        assert reaccelerated.times['train2'] == expected_times

    def test_groot_speedup_2trains_2(self, groot_2trains):
        disrupted = groot_2trains.add_delay('train1', 'A', 2)
        reaccelerated1 = disrupted.speedup(groot_2trains, 'train1', 'B')
        dispatched = reaccelerated1.add_delay('train2', 'A', 1)
        reaccelerated2 = dispatched.speedup(groot_2trains, 'train2', 'B')
        expected_times = {
            'A': (5, 8),
            'B': (7.5, 9.5),
            'C': (9, 12)
        }
        assert reaccelerated2.times['train2'] == expected_times
