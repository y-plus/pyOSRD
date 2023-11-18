import copy
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Agent(ABC):

    name: str

    def regulated(self, osrd):

        self.delayed = osrd.delayed()
        regulated = copy.deepcopy(self.delayed)
        regulated.simulation_json = os.path.join(
            'delayed',
            self.name,
            osrd.simulation_json
        )
        regulated.results_json = os.path.join(
            'delayed',
            self.name,
            osrd.results_json
        )
        regulated.delays_json = os.path.join(
            osrd.delays_json
        )

        self.write_stops_json(osrd)

        with open(
            os.path.join(osrd.dir, 'delayed', self.name, 'stops.json'), 'r'
        ) as f:
            stops = json.load(f)

        regulated.add_stops(
            stops=stops,
        )

        regulated.add_delays_in_results()

        return regulated

    @abstractmethod
    def stops(self, osrd) -> List[Dict[str, Any]]:
        pass

    def write_stops_json(self, osrd) -> None:
        directory = os.path.join(osrd.dir, 'delayed', self.name)

        if not os.path.exists(directory):
            os.mkdir(directory)
        with open(
            os.path.join(osrd.dir, 'delayed', self.name, 'stops.json'), 'w'
        ) as f:
            json.dump(self.stops(osrd), f)
