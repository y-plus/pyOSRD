import shutil
from dataclasses import dataclass

from pyosrd import OSRD
from pyosrd.agents import Agent


def test_base_class_agent():

    sim = OSRD(simulation='station_capacity2', dir='tmp2')
    sim.add_delay('train0', time_threshold=90, delay=280.)
    delayed = sim.delayed()

    @dataclass
    class AddStop(Agent):
        train: int
        position: float
        duration: float

        def stops(self, osrd) -> list[dict[str, any]]:
            print(self.delayed)
            return [{
                'train': self.train,
                'position': self.position,
                'duration': self.duration,
            }]

    regulated = sim.regulate(agent=AddStop('name', 0, 2500, 10))

    arrival_times = [
        s.points_encountered_by_train(0)[-1]['t_base']
        for s in (sim, delayed, regulated)
    ]

    assert arrival_times == sorted(arrival_times)
    shutil.rmtree('tmp2', ignore_errors=True)
