import copy
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pyosrd.delays import shift_train_departure, add_delay_between_points


@dataclass
class Agent(ABC):

    name: str

    def regulated(self: "Agent", osrd):

        self.delayed = osrd.delayed()
        regulated = copy.deepcopy(self.delayed)

        # regulated.simulation_json = os.path.join(
        #     'delayed',
        #     self.name,
        #     osrd.simulation_json
        # )


        for train, delay in self.departures_to_shift().items():
            shift_train_departure(regulated, train, delay)

        dispatching_delays = self.delays_to_add()

        for train, delays in dispatching_delays.items():
            points = [
                p
                for p in osrd.delayed().points_encountered_by_train(train)
                if p['type'] in ['detector', 'departure', 'arrival']
            ]
            for zone, delay in delays.items():
                limits = sorted(
                    [
                        p
                        for p in points
                        if p['id'] in zone.split('<->')
                    ],
                    key=lambda x: x['t_base']
                )

                if len(limits) == 1:
                    if points.index(limits[0]) == 1:
                        limits = [points[0]] + limits
                    else:
                        limits += [points[-1]]
                add_delay_between_points(
                    regulated, 
                    train,
                    *[limit['id'] for limit in limits],
                    delay
                )

        os.makedirs(
            os.path.join(osrd.dir, 'delayed', self.name),
            exist_ok=True
        )

        regulated.results_json = os.path.join(
            'delayed',
            self.name,
            osrd.results_json
        )
        regulated.delays_json = os.path.join(
            osrd.delays_json
        )
        with open(os.path.join(regulated.dir, regulated.results_json), 'w') as outfile:
            json.dump(regulated.results, outfile)

        return regulated


    @abstractmethod
    def departures_to_shift(
        self: "Agent",
    ) -> dict[str, float]:
        ...

    @abstractmethod
    def delays_to_add(
        self: "Agent",
    ) -> dict[str, dict[str, float]]:
        ...

    # @abstractmethod
    # def stops(self, osrd) -> list[dict[str, Any]]:
    #     ...

    # def write_stops_json(self, osrd) -> None:
    #     directory = os.path.join(osrd.dir, 'delayed', self.name)

    #     if not os.path.exists(directory):
    #         os.mkdir(directory)
    #     with open(
    #         os.path.join(osrd.dir, 'delayed', self.name, 'stops.json'), 'w'
    #     ) as f:
    #         json.dump(self.stops(osrd), f)
